from .utils import *
import argparse

class CLI_parser():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description = f'{tcolor["y"]("labdata")} - tools to manage data in an experimental neuroscience lab',
            usage = f''' labdata <command> [args]

Command to start the dashboard webpage:
            {tcolor["y"]("dashboard")}                          Starts the dashboard monitor webpage 

Data manipulation commands are:

            {tcolor["y"]("subjects")}                            List subjects
            {tcolor["y"]("sessions")} -a <subject>               List sessions 
            {tcolor["y"]("get")} -a <subject> -s <session>       Download data from one session if not already there
            {tcolor["y"]("put")} -a <subject> -s <session>       Copies a dataset to the server to be used
            {tcolor["y"]("clean")}                               Deletes files that are already added

Data analysis commands:

            {tcolor["g"]("run")} <analysis> -a <subject> -s <session>     Allocates and runs analysis, local, queued or on AWS
            {tcolor["g"]("task")} <compute_task_number>                   Runs an allocated analysis task                      

Other
            logpipe <compute_task_number>                Appends stdout log to a ComputeTask
            build-container                              Builds and uploads singularity/apptainer containers to S3            
            run-container                                Launches a container in execution mode

Server commands (don't run on experimental computers):
            {tcolor["r"]("upload")}                                       Sends pending data to S3 (applies upload rules)

            ''')
        
        parser.add_argument('command',
                            help= 'type: labdata2 <command> -h for help')

        args = parser.parse_args(sys.argv[1:2])
        command = args.command.replace('-','_') # can use - in command
        if not hasattr(self, command):
            print('The command [{0}] was not recognized. '.format(args.command))
            parser.print_help()
            exit(1)
        getattr(self,command)()  # Runs the following parser

    def dashboard(self):
        import subprocess as sub
        main_webpage_path = Path(__file__).parent / 'dashboard' / 'index.py'
        command = f'streamlit run {str(main_webpage_path)}'.split(' ')
        sub.run(command)
    
    def subjects(self):
        parser = argparse.ArgumentParser(
            description = 'List sessions and datatypes',
            usage = '''labdata subject -u <USER> -f <FILTER>''')
        parser.add_argument('-u','--user',
                            default = None,
                            type = str,
                            help= 'User name restriction')
        
        parser.add_argument('-f','--filter-name',
                            default = None,
                            type = str,
                            help= 'Filter for subject_name')
        
        parser.add_argument('-s','--filter-sex',
                            default = None,
                            type = str,
                            help= 'Filter for subject_sex')
        
        args = parser.parse_args(sys.argv[2:])

        from .schema import Subject,LabMember
        query = Subject()
        if not args.filter_name is None:
            query = query & f'subject_name LIKE "%{args.filter_name}%"'
        if not args.filter_sex is None:
            query = query & f'subject_sex LIKE "%{args.filter_sex}%"'
        if not args.user is None:
            if len(LabMember & dict(user_name = args.user)):
                query = query & f'user_name LIKE "%{args.user}%"'
            else:
                print(f'User name {args.user} not found.')
        subjects = pd.DataFrame(query)
        if not len(subjects):
            print('No subjects in the query.')
            return
        for uname in np.unique(subjects.user_name):
            ss = subjects[subjects.user_name == uname]
            sss = ('Experimenter \033[96m{first_name} {last_name}\033[0m [{user_name}]'.format(**(LabMember() & dict(user_name = uname)).fetch1()))
            print(sss)
            for i,s in ss.reset_index().iterrows():
                if np.mod(i,2):
                    c = '\033[96m'
                else:
                    c = '\033[91m'
                cc = '\033[0m'
                print(f'{c}\t{i+1}.{cc} {s.subject_name}\t{s.subject_sex}\t{s.subject_dob}\t{s.strain_name}\t')
            print('')

    def sessions(self):
        parser = argparse.ArgumentParser(
            description = 'List sessions and datatypes',
            usage = '''labdata sessions -a <SUBJECT>''')
        parser = self._add_default_arguments(parser,1)
            
        args = parser.parse_args(sys.argv[2:])
        from .schema import Subject, Session, Dataset
        for s in args.subject:
            subject_name = s
            datasets = pd.DataFrame((Dataset()*Session() &
                                     dict(subject_name = subject_name)).fetch())
            sessions = np.sort(np.unique(datasets.session_datetime.values))
            print(f'\n {s} - {len(sessions)} sessions - {len(datasets)} datasets')
            for ses in sessions:
                dsets = datasets[datasets.session_datetime == ses]
                print(f'\t {tcolor["c"](dsets.iloc[0].session_name)}')
                for i,t in dsets.iterrows():
                    if t.dataset_type is None:
                        print(f'\t\t *{t.dataset_name}')
                    else:
                        print(f'\t\t {t.dataset_type} - {t.dataset_name}')
    
    def get(self):
        parser = argparse.ArgumentParser(
            description = 'Download data from one or multiple sessions',
            usage = '''labdata sessions -a <SUBJECTS> -s <SESSIONS>''')
        parser = self._add_default_arguments(parser,3)
        
        # TODO: Add an argument to include files that match a pattern..
        
        args = parser.parse_args(sys.argv[2:])
        from .schema import Subject, Session, Dataset, File
        keys = []
        # do all combinations of sessions and datasets
        if not args.subject is None:
            for a in args.subject:
                keys.append(dict(subject_name = a))
            if not args.session is None:
                for ses in args.session:
                    if len(keys):
                        for k in keys:
                            k['session_name'] = ses
                    else:
                        keys.append(dict(session_name = ses))
        if not args.datatype is None:
            for d in args.datatype:
                if len(keys):
                    for k in keys:
                        k['dataset_type'] = d
                else:
                    keys.append(dict(dataset_name = d))
        # download the files
        (File() & (Dataset.DataFiles() & keys).proj()).get()
        
    def put(self):
        parser = argparse.ArgumentParser(
            description = 'Copies data to the server to be uploaded [THIS DOES NOT UPLOAD TO THE CLOUD]',
            usage = '''labdata put -a <SUBJECT> -s <SESSION>''')
        
        parser = self._add_default_arguments(parser)
        parser.add_argument('filepaths', action = 'store',
                            default = [''], type = str, nargs = '+')
        parser.add_argument('-t','--datatype-name',
                            action = 'store',
                            default = None, type = str, nargs = 1)
        parser.add_argument('-r','--rule',
                            action = 'store',
                            default = None, type = str, nargs = 1)
        parser.add_argument('--overwrite', action = 'store_true',
                            default = False)
        parser.add_argument('--ask', action = 'store_true',
                            default = False)
        parser.add_argument('--select',
                            action = 'store_true',
                            default = False)
        
        args = parser.parse_args(sys.argv[2:])
        if args.select: # open a gui to select files, not working at the moment
            from .widgets import QApplication, LABDATA_PUT
            app = QApplication(sys.argv)
            w = LABDATA_PUT()
            sys.exit(app.exec_())
        else:
            from .widgets import QApplication, ServerCopyWidget
            app = QApplication(sys.argv)
            filepaths = args.filepaths
            if len(filepaths) == 1:
                if Path(filepaths[0]).is_dir(): # then select all files inside the folder
                    filepaths = list(Path(filepaths[0]).rglob('**/*'))
                    filepaths = list(filter(lambda f: f.is_file(),filepaths))
            w = ServerCopyWidget(src_filepaths = filepaths,
                                 upload_rule = args.rule,
                                 user_confirmation = args.ask,
                                 overwrite = args.overwrite)
            app.exit()
            #sys.exit(app.exec_())
    def clean(self):
        parser = argparse.ArgumentParser(
            description = 'Releases local storage space.',
            usage = '''labdata clean -f "ephys"''')
        parser.add_argument('-f','--filter',action = 'store',default = [], type = str, nargs = '+')
        parser.add_argument('--dry-run',action = 'store_true', default = False)
        args = parser.parse_args(sys.argv[2:])
        from .copy import clean_local_path

        
        deleted,kept = clean_local_path(filterkeys = args.filter, dry_run = args.dry_run)
        print(deleted,kept)
    def run(self):
        parser = argparse.ArgumentParser(
            description = 'Allocates or runs an analysis',
            usage = '''labdata run <ANALYSIS> -a <SUBJECT> -s <SESSION>''')
        parser.add_argument('analysis',action = 'store',default = '',type = str)
        parser.add_argument('-j','--job',action = 'store',default = None, type = int)
        parser.add_argument('-t','--target',action = 'store', default = prefs['compute']['default_target'], type = str)
        parser.add_argument('--force-submit',action = 'store_true', default = False)
        
        parser = self._add_default_arguments(parser)
        secondary_args = []
        argum = sys.argv[2:]
        if '--' in sys.argv:
            argum = sys.argv[2:sys.argv.index('--')]
            secondary_args = sys.argv[sys.argv.index('--'):]
        args = parser.parse_args(argum)
        from .compute import parse_analysis, run_analysis
        if args.analysis == 'queue':
            from .compute.schedulers import check_queue
            if args.target == 'local':
                print('"local" target does not have a scheduler.')
            queue = check_queue(target = args.target)
            if len(queue) == 0:
                print(f"Target: {tcolor['m'](args.target)} queue has no jobs.")
                return
            print(f"Target: {tcolor['m'](args.target)}")
            for j in queue:
                if j['state'] in ["R","RUNNING"]:
                    cc = tcolor['g']
                else:
                    cc = tcolor['r']
                print(f"\t {j['jobid']} {j['name']} {cc('running')} time: {tcolor['y'](j['time'])}\n\t\tpartition: {j['partition']} node: {j['nodelist(reason)']} ")

            return
        # parse analysis will check if the analysis is defined
        jobids,obj = parse_analysis(analysis = args.analysis,
                                    job_id = args.job, 
                                    subject = args.subject,
                                    session = args.session,
                                    datatype = args.datatype,
                                    secondary_args = secondary_args,
                                    force_submit = args.force_submit,
                                    full_command = ' '.join(sys.argv[1:]))
        if not len(jobids):
            print('Nothing to run.')
            return
        target = args.target
        run_analysis(target,jobids, obj)

    def task_reset(self):
        parser = argparse.ArgumentParser(
            description = 'Reset a task in the ComputeTask so the job can be ran again',
            usage = '''labdata task_reset <JOB_ID> ''')
        parser.add_argument('job_id', action = 'store', type = int, nargs='+')
        parser.add_argument('-t','--target', action = 'store', default = None, type = str)
        parser.add_argument('--resubmit', action = 'store_true', default = False)
        parser.add_argument('--clear-all', action = 'store_true', default = False)

        args = parser.parse_args(sys.argv[2:])
        if args.clear_all:
            print('Deleting all compute tasks - please confirm.')
            from .schema import ComputeTask
            ComputeTask.delete()
            sys.exit()
        for job_id in args.job_id:
            from .schema import ComputeTask
            jb = (ComputeTask() & f'job_id = {job_id}').fetch(as_dict = True)
            if not len(jb):
                raise(ValueError(f'ComputeTask job_id: {job_id} not found.'))
            jb = jb[0]
            ComputeTask.update1(dict(job_id = job_id,
                                    task_waiting = 1,
                                    task_status = 'WAITING',
                                    task_starttime = None,
                                    task_endtime = None))
            if args.resubmit:
                # then re-submit the compute task
                from .compute.utils import load_analysis_object, run_analysis
                obj = load_analysis_object(jb['task_name'])(None)
                if not args.target is None:
                    target = args.target
                else:
                    target = jb['task_target'].split('@')[0]
                run_analysis(target,[job_id],obj)
                    
    def task(self):
        parser = argparse.ArgumentParser(
            description = 'Runs a ComputeTask',
            usage = '''labdata task <JOB_ID> ''')
        parser.add_argument('job_id',action = 'store',default = None,type = int)
        args = parser.parse_args(sys.argv[2:])
        job_id = args.job_id
        if not job_id is None:
            from .compute import handle_compute
            task = handle_compute(job_id)
            task.compute()

    def upload(self):
        parser = argparse.ArgumentParser(
            description = 'Runs an UploadTask',
            usage = '''labdata upload <JOB_ID> (optional) ''')
        parser.add_argument('job_id',action = 'store',default = [], type = int, nargs = '*')
        parser.add_argument('--all-hosts',action = 'store_true',default = False)
        parser.add_argument('--reset-failed',action = 'store_true',default = False)
        parser.add_argument('--queue',action='store_true',default = False)
        args = parser.parse_args(sys.argv[2:])
        if args.queue:
            from .schema import UploadJob
            j = UploadJob & 'job_status = "WORKING"'
            if len(j):
                print(tcolor['m']("++++++++++++++++++++ JOBS IN PROGRESS ++++++++++++++++++++"))
                print(j)
            j = UploadJob & 'job_status = "FAILED"' & 'job_waiting = 0'
            if len(j):
                print(tcolor['r']("++++++++++++++++++++ FAILED JOBS ++++++++++++++++++++"))
                print(j)
            j = UploadJob & 'job_waiting = 1'
            if len(j):
                print(tcolor['y']("++++++++++++++++++++ WAITING JOBS ++++++++++++++++++++"))
                print(j)
            j = UploadJob & 'job_status = "COMPLETED"'
            lenj = len(j)
            if (lenj < 10) & (lenj > 0):
                print(tcolor['g']("++++++++++++++++++++ COMPLETED JOBS ++++++++++++++++++++"))
                print(j)
            else:
                print(tcolor['g'](f"++++++++++++++++++++ {lenj} COMPLETED JOBS ++++++++++++++++++++"))
            return
        job_ids = args.job_id
        
        if args.reset_failed:
            from .schema import UploadJob
            print(len(job_ids))
            if not len(job_ids):
                jbs = (UploadJob() & 'job_status = "FAILED"').proj().fetch(as_dict=True)
            else:
                jbs = (UploadJob() & [f'job_id = {i}' for i in job_ids]).proj().fetch(as_dict=True)
            for jb in jbs:
                jb['job_waiting'] = 1
                jb['job_status'] = "WAITING"
                UploadJob().update1(jb)
        keys = []
        for j in job_ids:
            keys.append(dict(job_id = j))
            if not args.all_hosts:
                keys[-1]['job_host'] = prefs['hostname']
        from .rules import process_upload_jobs
        if len(keys):
            task = process_upload_jobs(keys)
        else:
            key = dict(job_waiting = 1)
            if not args.all_hosts:
                key['job_host'] = prefs['hostname']
            tasks = process_upload_jobs(key)

    def logpipe(self):
        parser = argparse.ArgumentParser(
            description = 'Sends the stdout to a log',
            usage = '''labdata logpipe <JOB_ID> ''')
        parser.add_argument('job_id',action = 'store',default = None,type = int)
        parser.add_argument('-i','--refresh-period',action = 'store',default = 5., type = float)
        args = parser.parse_args(sys.argv[2:])
        job_id = args.job_id
        refresh_period = args.refresh_period
        from .schema import ComputeTask
        from time import time as toc
        tic = toc()
        if job_id is None:
            print('No task specified.')
        else:
            # Check first if the job exists
            t = ComputeTask & f'job_id = {job_id}'
            if not len(t):
                print(f'Could not find ComputeTask: {job_id}.')
                return
            print(f'Appending stdout to ComputeTask [{job_id}] ')
            
        def handle_line(line,tic):
            if toc()-tic > refresh_period:
                tic = toc()
                log = t.fetch('task_log')[0]
                if not line is None:
                    if log is None:
                        log = line
                    else:
                        log += '\n' + line
                if len(log) > 2000:
                    log = log[-1999:]
                ComputeTask().update1(dict(job_id = job_id, task_log = log))
            if not line is None:
                print(line,end = '',flush = True)         
            return line,tic
        from select import select            
        while True:
            if select([sys.stdin],[],[],refresh_period):
                line,tic = handle_line(sys.stdin.readline(),tic)
            if not line:
                print('Pipe closed.')
                break
    
    def run_container(self):
        '''
        Runs a container
        '''
        parser = argparse.ArgumentParser(
            description = 'Run a container',
            usage = '''labdata run_container <container> ''')
        parser.add_argument('container_name',
                            action = 'store',
                            type = str)
        parser.add_argument('-t','--target',action = 'store', default = prefs['compute']['default_target'], type = str)
        parser.add_argument('--jupyter', action = 'store_true', default = False)
        parser.add_argument('--cuda',action = 'store_true', default = False)

        args = parser.parse_args(sys.argv[2:])
        container = args.container_name
        container_file = None
        cmd = None
        target = args.target
        if target in ['local','slurm']:
            container_store = Path(prefs['compute']['containers']['local'])
            container_file = (container_store/container).with_suffix('.sif')
            if not container_file.exists():
                print( f"Container {tcolor['r'](container)} not found in {tcolor['r'](container_store)}")
                return 
        
        if args.jupyter:
            cmd = "jupyter lab"
        
        if not cmd is None:
            from .compute.singularity import run_on_apptainer
            launchcmd = run_on_apptainer(container_file,
                                         command = cmd,
                                         cuda = args.cuda,
                                         bind_from_prefs = True,
                                         launch_cmd = 'run', # use exec for running ephemeral
                                         dry_run = True)
            print(launchcmd)

    def build_container(self):
        '''
        Build containers and upload to S3.
        '''
        parser = argparse.ArgumentParser(
            description = 'Builds container(s).',
            usage = '''labdata build_container <container_file> ''')
        parser.add_argument('container_file',
                            action = 'store',
                            type = str,
                            nargs = '+')
        parser.add_argument('--upload',
                            action='store_true',
                            default=False)
        parser.add_argument('--skip-build',
                            action='store_true',
                            default=False)
        args = parser.parse_args(sys.argv[2:])
        container_files = args.container_file
        destination = Path(prefs['compute']['containers']['local'])
        built = []
        for definition_file in container_files:
            definition_file = Path(definition_file).resolve().absolute()
            container = Path(destination/definition_file.stem).with_suffix('.sif')
            cmd = f'apptainer build --fakeroot --force {container} {definition_file}'
            if args.skip_build:
                print(f'Skipping build: {cmd}')
            else:
                os.system(cmd)
            if container.exists():
                built.append(container)
        if args.upload:
            from .s3 import copy_to_s3
            storage_name = prefs['compute']['containers']['storage']
            dst = ['containers/' + b.name for b in built]
            print('Uploading containers to s3, this may take a while.')
            copy_to_s3(built,dst,storage_name = storage_name)
            print(f'Uploaded {dst} to storage {storage_name}.')

    def _add_default_arguments(self, parser,level = 3):
        if level >= 1:
            parser.add_argument('-a','--subject',
                                action='store',
                                default=None, type=str,nargs='+')
        if level >= 2:

            parser.add_argument('-s','--session',
                                action='store',
                                default=None, type=str,nargs='+')
        if level >= 3:
            parser.add_argument('-d','--datatype',
                            action='store',
                            default=None, type=str,nargs='+')
        return parser
        
    def _get_default_arg(self,argument,cli_arg = 'submit', default = None):
        # checks if there is a default in the options
        if not f'{cli_arg}_defaults' in labdata_preferences.keys():
            return default # no defaults
        if labdata_preferences[f'{cli_arg}_defaults'] is None:
            return default # not defined dict
        if not argument in labdata_preferences[f'{cli_arg}_defaults'].keys():
            return default  # not defined
        return labdata_preferences[f'{cli_arg}_defaults'][argument]

def main():
    CLI_parser()
