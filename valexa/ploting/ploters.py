import json
from typing import Dict, List

from valexa.core.profiles import (DEFAULT_ACCEPTANCE as ACCEPTANCE, 
    DEFAULT_TOLERANCE as TOLERANCE, Profile, make_profiles)
from valexa.core.xlsx import XlsxHandler
from valexa.ploting.plotly.canvas import ProfilePlotCanvas


class PloterData:

    def __init__(self, file: str or File, handler=XlsxHandler, 
            tolerance_limit: int=TOLERANCE, acceptance_limit: int=ACCEPTANCE):
        
        self.tolerance_limit = tolerance_limit
        self.acceptance_limit = acceptance_limit
        self.handler = handler

        self.load_data(file)

    def load_data(self, file: str or File) -> None:
        handler = self.handler(file)

        self.profiles = make_profiles(
            handler.get_calibration_data(), 
            handler.get_validation_data(), 
            self.tolerance_limit, 
            self.acceptance_limit
        )
