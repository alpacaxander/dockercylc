"""
Utilities for parallel processing.

"""

import itertools
import logging

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())

ALL_PROCESSORS = -1
DEFAULT_PROCESSORS = -999
DEFAULT_CPU_FRACTION = 2
FINISHED       = None

#---------------------------------------------------------------------
# Generic "map" implementation that permits multiprocessing
#---------------------------------------------------------------------
def get_task_mapper(parallel_procs=ALL_PROCESSORS):
    """
    Return a mapping method that will process arguments.

    Whether this processes arguments in parallel or serially depends on
    the input arguments.  If the input value is 0 *or* if something
    goes pear-shaped in the setup of the parallel processing, the resulting
    mapper will be serial.  Otherwise, use the number of processes supplied.

    """

    # Get the number of processes to use
    num_procs = get_num_processors(parallel_procs)

    # Set up the task mapper
    if num_procs:
        LOG.info('Attempting parallel processing with %d processes.', num_procs)
        if check_multiprocessing:
            import multiprocessing
            pool   = multiprocessing.Pool(processes=num_procs)
            mapper = pool.map
        else:
            LOG.warning('Failed to initialize parallel processing.')
            LOG.warning('Falling back to serial mode.')
            mapper = map
    else:
        LOG.info('Using serial processing.')
        mapper = map

    return mapper


#----------------------------------------------------------------------
# Generic producer/consumer implementation that permits multiprocessing
#----------------------------------------------------------------------
def task_mapper(task_function, task_iterable, parallel_procs=None):
    """
    Return the results for the function that were mapped with the iterable for
    parallel processing. Setup the multiprocessing map with get_task_mapper.

    """

    num_procs = get_num_processors(parallel_procs)

    if num_procs == 0:
        LOG.debug('Using serial task processor...')
        return serial_pc(task_function, task_iterable)
    else:
        LOG.debug('Using %d-parallel task processors...', num_procs)
        return parallel_pc(task_function, task_iterable, num_procs)


def check_multiprocessing():
    """
    Check whether this environment will allow multiprocessing. 

    """

    try:
        import multiprocessing
    except ImportError:
        return False
    return True


def get_num_processors(parallel_procs=None):
    """
    Return number of processor allowed by user input and multiprocessing. 

    """

    LOG.debug('Checking to make sure multiprocessing works...')
    if check_multiprocessing:
        import multiprocessing
    else:
        parallel_procs = 0
        LOG.warning('Failed to import multiprocessing - switch to serial.')

    if parallel_procs is None or parallel_procs < 0:
        LOG.info('Attempting to auto-detect CPU count...')
        try: 
            num_procs = multiprocessing.cpu_count()
        except:
            LOG.warning('CPU Auto-detect failed - fallback to serial mode.')
            num_procs = 0
        if num_procs > 0:
            if parallel_procs == DEFAULT_PROCESSORS:
                num_procs = min(num_procs / DEFAULT_CPU_FRACTION, 12)
                LOG.info('Default CPU selected, using {0} processors...'.format(num_procs))
            else:
                LOG.info('ALL CPU selected, using {0} processors...'.format(num_procs))
    else:
        num_procs = parallel_procs
        LOG.debug('Using {0} processors...'.format(num_procs))

    return num_procs





def parallel_pc(task_function, task_iterable, nproc):
    """
    Apply task_function to each element of task_iterable using a parallel
    producer/consumer algorithm over nproc processes.  

    Skip over input data where an error occurs.

    """
    import multiprocessing

    work_queue    = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()

    loader = get_worker_processes(
        _load_data,
        (task_iterable, work_queue, nproc),
        nproc=1,
        allow_scalar=True
    )
    workers = get_worker_processes(
        _process_data,
        (task_function, work_queue, results_queue),
        nproc=nproc,
    )

    # Start the processing
    LOG.debug('Starting producer process...')
    loader.start()
    LOG.debug('Starting consumer processes...')
    for worker in workers:
        worker.start()

    # Convert the results to a list - there is one 'finished' entry
    # from each process, so need to get them all.  Need to interleave
    # this portion with the actual processing (i.e. before the join)
    # to avoid the pipe used by the Queue filling up and hanging the
    # joins (see, e.g. http://stackoverflow.com/q/11854519/24895)
    LOG.info('Converting results to a final list...')
    percent_threshold = 0
    task_results      = []
    for _ in range(nproc):
        for element in iter(results_queue.get, FINISHED):
            task_results.append(element)
            len_task_iterable = len(list(task_iterable))
            if len_task_iterable < 1:
                len_task_iterable = 1
            if (100*len(task_results)/len_task_iterable) > percent_threshold:
                LOG.info('{0:.0f}% - tasks complete'.format(percent_threshold))
                percent_threshold += 5
    LOG.info('{0:.0f}% - tasks complete'.format(100))

    LOG.debug('Waiting for loader to finish...')
    loader.join()
    LOG.debug('Loader finished...')

    LOG.debug('Waiting for workers to finish...')
    for id, worker in enumerate(workers):
        worker.join()
        LOG.debug('Worker %d finished...',id)
    LOG.debug('All workers finished...')

    return task_results


def get_worker_processes(f, args, nproc=None, allow_scalar=False):
    """
    Return a set of worker processes for a given function and argument set.

    If no process count is given, use the CPU count of the current machine.

    If allow_scalar is set to True, allow this routine to return a single
    process instead of list-of-length-1 containing a single process.

    """

    import multiprocessing
    num_procs = get_num_processors(nproc)

    workers = [
        multiprocessing.Process(target=f, args=args) for _ in range(num_procs)
    ]
    if allow_scalar and len(workers) == 1:
        return workers[0]
    else:
        return workers


def _load_data(l, q, nproc):
    """
    Wrapper function to load the data from the iterable l into queue q,
    assuming that there will be nproc processes working on the queue.

    This is the "producer" in the producer/consumer algorithm.

    """
    for element in l:
        q.put(element)
    for _ in range(nproc):
        q.put(FINISHED)


def _process_data(f, work_queue, results_queue):
    """
    Wrapper function that will apply the function f to each element of the
    work queue and place the results in the results queue.

    This is the "consumer" in the producer/consumer algorithm.

    """
    for element in iter(work_queue.get, FINISHED):
        try:
            results_queue.put(f(element))
        except Exception, work_error:
            LOG.critical('parallel_pc Error: {0}\n\n\tconfig settings {1}\n'.format(work_error, element))
    results_queue.put(FINISHED)
