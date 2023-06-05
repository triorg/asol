import os
import json
import sys
from dataclasses import dataclass, asdict
import logging
from typing import Optional, Any
from . import logger
logerr = logging.getLogger(__name__)
logerr.addHandler(logger.handler_stderr)
import re
from datetime import datetime
import shutil

def count_files_norecurse(directory):
    return len(os.listdir(directory))

### stdout
@dataclass
class filemove:
    source: str
    target: str


class Runner:
    def __init__(self,pars):
        self.params=pars
        files=os.listdir(pars.input)
        self.files=files
        self.filescount=len(files)

    def params_debug(self):
        print(json.dumps(self.params.__dict__))

    def params_check(self):
        logerr.info("checking parameters")
        self.params=params_check(self.params)
        logerr.info(f"Files {self.filescount} to process")

    def simulate(self):
        self.params=params_check(self.params)
        logerr.info(f"Files {self.filescount} to process")
        processed=0
        for f in self.files:
            fdate=date_from_filename(f)
            fsource=os.path.join(self.params.input,f)
            ftarget=os.path.join(self.params.output,"hello")
            outinfo=filemove(source=fsource,target=ftarget)
            jdate=date_from_json(fsource)
            # print("jdate",jdate)
            # print("fdate",fdate)
            if jdate != fdate:
                logerr.error(f"date differs: {fsource}")
                continue
            if jdate is None or fdate is None:
                ### error treated when parsing values from filename or json
                continue
            print(f"processing: {fsource}")
            dstdir=destination_path(jdate)
            dstdir=os.path.join(self.params.output,dstdir)
            print(dstdir)

            # try:
                # shutil.move(source_path, target_path)
                # print(f"File '{filename}' moved successfully from '{source_dir}' to '{target_dir}'.")
            # except IOError as e:
                # print(f"Error while moving the file: {e}")

            processed+=1

        if processed == self.filescount:
            logerr.info(f"Success: processed {processed}/{self.filescount} files")
        if processed != self.filescount:
            logerr.error(f"Failed: processed {processed}/{self.filescount} files")

            # else:
                # print("jdate",jdate)
                # print("fdate",fdate)
            # if jdate is None or fdate != jdate:

def move_file(src: str,dst: str,dryrun: bool,overwrite: bool) -> bool:
    err_file=f"input_file: {src}, error moving,"
    if os.path.exists(dst):
        if not overwrite:
            logerr.error(f"{err_file} file already exists: {dst}")
        return False
        logerr.warn(f"{err_file} file already exists: {dst}")
    try:
        if not dryrun:
            shutil.move(src,dst)
        return True
    except IOError as e:
        logerr.error(f"{err_file} exception {e}")
        return False

def destination_path(date: datetime) -> str:
    week_number=date.isocalendar()[1]
    wstring=f"W{week_number:02d}"
    year=str(date.year)
    month=date.month
    day=date.day
    daynum=date.weekday()+1
    fname=f"{month:02d}-{day:02d}_{daynum:01d}.json"
    dstdir=os.path.join(year,wstring,fname)
    return dstdir

def parse_date(date_string: str) -> datetime:
    try:
        format_string = "%Y-%m-%d"
        parsed_date = datetime.strptime(date_string, format_string)
        return parsed_date
    except ValueError:
        return none

def date_from_filename(filename: str) -> datetime:
    # Use regular expression to extract date from filename
    pattern = r"\d{4}-\d{2}-\d{2}"
    match = re.search(pattern, filename)
    if match:
        fdate=parse_date(match.group())
        return fdate
    else:
        logerr.error("filename.date: no valid date")
        return None

def date_from_json(input_file: str) -> datetime:
    err_json=f"input_file: {input_file}, error parsing,"
    try:
        with open(input_file, 'r') as file:
            try:
                json_data = json.load(file)
                jdatestr=json_data['date']
                if jdatestr is None:
                    logerr.error(f"{err_json} json.date: None")
                    return None
                jdate=parse_date(jdatestr)
                if jdate is None:
                    logerr.error(f"{err_json} json.date: invalid date")
                    return None
                return jdate
            except json.JSONDecodeError as e:
                logerr.error(f"{err_json} json.date: invalid json, {e}")
                return None
            except Exception as e:
                logerr.error(f"{err_json} json.date: exception, {e}")
                return None
    except FileNotFoundError:
        logerr.error(f"{err_json} json.date: file not found")
        return None
    except PermissionError:
        logerr.error(f"{err_json} json.date: no permission error")
        return None
    except Exception as e:
        logerr.error(f"{err_json} json.date: exception, {e}")
        return None

def params_check(pars):
    """ Check that parametrs are valid """
    ### validate input dir
    if not os.access(pars.input, os.R_OK):
        raise ValueError(f"source dir not readable: {pars.input}")

    ### validate output dir
    if not os.path.exists(pars.output):
        raise ValueError(f"path does not exists: {pars.output}")
    if not os.path.isdir(pars.output):
        raise ValueError(f"path is not directory: {pars.output}")
    if not os.access(pars.output, os.W_OK):
        raise ValueError(f"output directory not writable: {pars.output}")
    if os.listdir(pars.output):
        logerr.warn(f"output directory not empty: {pars.output}")
        # pars.output=os.path.join(pars.output,"target")
    # if os.listdir(pars.output):
        # logerr.warn(f"directory not empty: {pars.output}")
    return pars


