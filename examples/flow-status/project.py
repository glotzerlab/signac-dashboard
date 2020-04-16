from flow import FlowProject


class Project(FlowProject):
    pass


@Project.label()
def current_step(job):
    return 'Current step: {}'.format(job.doc['step'])


@Project.label()
def is_even(job):
    if job.doc['step'] % 2 == 0:
        return True


@Project.label()
def is_odd(job):
    if job.doc['step'] % 2 == 1:
        return True


if __name__ == '__main__':
    Project().main()
