import time

from fire import Fire
from datetime import datetime, timedelta
from traxix.rsq import RSQ, Const, Conditions


def create_rsq(mongo_url="localhost:27017", db_name="rsq"):
    return RSQ(mongo_url=mongo_url)


def len_cats(rsq, todo, inprogress, done, fail):
    assert len(rsq.list_task(state=Const.State.TODO)) == todo
    assert len(rsq.list_task(state=Const.State.INPROGRESS)) == inprogress
    assert len(rsq.list_task(state=Const.State.DONE)) == done
    assert len(rsq.list_task(state=Const.State.FAIL)) == fail
    assert rsq.count() == (todo + inprogress + done + fail)


def test_trivial():
    # cleanup
    rsq = create_rsq()
    rsq.remove()
    len_cats(rsq=rsq, todo=0, inprogress=0, done=0, fail=0)

    task_id = rsq.push(random_key="random_value")
    len_cats(rsq=rsq, todo=1, inprogress=0, done=0, fail=0)
    todos = rsq.list_task(state=Const.State.TODO)

    assert todos[0][Const.DATA] == {"random_key": "random_value"}

    # Consume task
    work = rsq.pull()

    len_cats(rsq=rsq, todo=0, inprogress=1, done=0, fail=0)

    assert work[Const.ID] == task_id
    assert work[Const.DATA] == {"random_key": "random_value"}

    rsq.done(_id=work[Const.ID], result=42)
    len_cats(rsq=rsq, todo=0, inprogress=0, done=1, fail=0)


def test_cond():
    rsq = create_rsq()
    rsq.remove()
    len_cats(rsq=rsq, todo=0, inprogress=0, done=0, fail=0)

    time_in = datetime.utcnow() + timedelta(seconds=1)
    conditions = Conditions(time_in=time_in)
    task_id = rsq.push(conditions=conditions, random_key="random_value")

    # time_in not ready
    work = rsq.pull()
    assert work is None
    time.sleep(2)

    # time_in ready
    work = rsq.pull()
    assert work is not None

    # time_out out
    conditions = Conditions(time_out=time_in)
    task_id = rsq.push(conditions=conditions, random_key="random_value2")
    work = rsq.pull()
    assert work is None

    # time_in and time_out
    time_in = datetime.utcnow()
    time_out = time_in + timedelta(seconds=1)
    conditions = Conditions(time_in=time_in, time_out=time_out)
    task_id = rsq.push(conditions=conditions, random_key="random_value3")


def test_who():
    rsq = create_rsq()
    rsq.remove()
    task_id = rsq.push(random_key="random_value")

    work = rsq.pull(who="dr")
    tasks = rsq.list_task(state=Const.State.INPROGRESS)
    assert len(tasks) == 1
    assert tasks[0][Const.WHO] == "dr"


def test_additional_query():
    rsq = create_rsq()
    rsq.remove()
    additional_query = {f"{Const.DATA}.docker": {"$exists": True}}
    task_id = rsq.push(
        docker="31415926535..dkr.ecr.eu-west-3.amazonaws.com/compkisstador:1P4QGDN19L",
        random_key="random_value4",
    )
    task_id = rsq.push(random_key="random_value5")

    task_list = rsq.list_task(additional_query=additional_query)
    assert len(task_list) == 1
    assert task_list[0][Const.DATA]["random_key"] == "random_value4"

    work = rsq.pull(who="letsthedogout", additional_query=additional_query)

    assert work is not None
    print(work)
    assert work[Const.DATA]["random_key"] == "random_value4"

    work = rsq.pull(
        who="letsthedogout",
        additional_query=additional_query,
    )
    assert work is None

    work = rsq.pull(who="letsthedogout")
    assert work is not None


def test_reset():
    rsq = create_rsq()
    rsq.remove()
    task_id = rsq.push(random_key="random_value6")

    len_cats(rsq=rsq, todo=1, inprogress=0, done=0, fail=0)
    work = rsq.pull(who="dr")
    len_cats(rsq=rsq, todo=0, inprogress=1, done=0, fail=0)
    rsq.reset(_id=task_id)

    len_cats(rsq=rsq, todo=1, inprogress=0, done=0, fail=0)
    rsq.push(random_key="random_value8")
    rsq.push(random_key="random_value9")
    rsq.pull()
    rsq.pull()
    len_cats(rsq=rsq, todo=1, inprogress=2, done=0, fail=0)
    rsq.reset(state=Const.State.FAIL)
    len_cats(rsq=rsq, todo=0, inprogress=0, done=0, fail=3)


def test_misc():
    rsq = create_rsq()
    rsq.remove()

    task_id = rsq.push(random_key="random_value7")
    task = rsq.list_task(_id=task_id)
    assert len(task) == 1

    rsq.remove(_id=task_id)
    len_cats(rsq=rsq, todo=0, inprogress=0, done=0, fail=0)

    conditions = Conditions()
    assert conditions.to_query() == {}


def test_result():
    rsq = create_rsq()
    rsq.remove()

    task_id = rsq.push(random_key="random_value8")
    work = rsq.pull()
    rsq.done(_id=work[Const.ID], result=42)

    result = rsq.list_task(_id=task_id)
    assert len(result) == 1
    assert result[0][Const.RESULT] == 42


if __name__ == "__main__":
    Fire()  # pragma: no cover
