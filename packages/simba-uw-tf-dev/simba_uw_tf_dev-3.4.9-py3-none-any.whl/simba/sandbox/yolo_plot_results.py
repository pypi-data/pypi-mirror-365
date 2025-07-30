





from tkinter import *

import numpy as np
from simba.data_processors.cuda.utils import _is_cuda_available
from simba.mixins.pop_up_mixin import PopUpMixin
from simba.ui.tkinter_functions import (CreateLabelFrameWithIcon, FileSelect, FolderSelect, SimBADropDown)
from simba.utils.checks import (check_file_exist_and_readable, check_if_dir_exists)
from simba.utils.enums import Options, PackageNames
from simba.utils.errors import SimBAGPUError, SimBAPAckageVersionError
from simba.utils.read_write import find_core_cnt, get_pkg_version, str_2_bool, find_files_of_filetypes_in_directory, get_video_meta_data
from simba.ui.tkinter_functions import SimbaButton
from simba.model.yolo_pose_inference import YOLOPoseInference

MAX_TRACKS_OPTIONS = ['None', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
CORE_CNT_OPTIONS = list(range(1, find_core_cnt()[0]))
THRESHOLD_OPTIONS = np.arange(0.1, 1.1, 0.1).astype(np.float32)
SIZE_OPTIONS = list(range(1, 21, 1))
SIZE_OPTIONS.insert(0, 'AUTO')

class YoloPlotSingleVideoPopUp(PopUpMixin):

    def __init__(self):
        gpu_available, gpus = _is_cuda_available()
        if not gpu_available:
            raise SimBAGPUError(msg=f'Cannot train YOLO pose-estimation model. No NVIDA GPUs detected on machine', source=self.__class__.__name__)
        ultralytics_version = get_pkg_version(pkg=PackageNames.ULTRALYTICS.value)
        if ultralytics_version is None:
            raise SimBAPAckageVersionError(msg=f'Cannot train YOLO pose-estimation model: Could not find ultralytics package in python environment',  source=self.__class__.__name__)

        PopUpMixin.__init__(self, title="TRAIN YOLO POSE ESTIMATION MODEL", icon='ultralytics_2')
        settings_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="SETTINGS", icon_name='settings')


        self.data_path = FileSelect(parent=settings_frm, fileDescription='DATA PATH (CSV):', lblwidth=35,  entry_width=45, file_types=[("YOLO CSV RESULT", ".csv")])
        self.video_path = FileSelect(parent=settings_frm, fileDescription='VIDEO PATH:', lblwidth=35,  entry_width=45, file_types=[("YOLO CSV RESULT", Options.ALL_VIDEO_FORMAT_OPTIONS.value)])
        self.save_dir = FolderSelect(settings_frm, folderDescription="SAVE DIRECTORY:", lblwidth=35, entry_width=45)
        self.core_cnt_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=CORE_CNT_OPTIONS, label="CPU CORE COUNT:", label_width=35, dropdown_width=40, value=int(max(CORE_CNT_OPTIONS) / 2))
        self.bbox_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=['TRUE', 'FALSE'], label="SHOW BOUNDING BOXES:",  label_width=35, dropdown_width=40, value='FALSE')
        self.verbose_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=['TRUE', 'FALSE'], label="VERBOSE:",  label_width=35, dropdown_width=40, value='TRUE')
        self.threshold_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=THRESHOLD_OPTIONS, label="THRESHOLD:",  label_width=35, dropdown_width=40, value=0.5)
        self.thickness_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=SIZE_OPTIONS, label="LINE THICKNESS:",  label_width=35, dropdown_width=40, value='AUTO')
        self.circle_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=SIZE_OPTIONS, label="CIRCLE SIZE:", label_width=35, dropdown_width=40, value='AUTO')

        self.create_run_frm(run_function=self.run)


    def run(self):
        pass




