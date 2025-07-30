"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4988 import (
        CalculateFullFEResultsForMode,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4989 import (
        CampbellDiagramReport,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4990 import (
        ComponentPerModeResult,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4991 import (
        DesignEntityModalAnalysisGroupResults,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4992 import (
        ModalCMSResultsForModeAndFE,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4993 import (
        PerModeResultsReport,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4994 import (
        RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4995 import (
        RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4996 import (
        RigidlyConnectedDesignEntityGroupModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4997 import (
        ShaftPerModeResult,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4998 import (
        SingleExcitationResultsModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting._4999 import (
        SingleModeResults,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4988": [
            "CalculateFullFEResultsForMode"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4989": [
            "CampbellDiagramReport"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4990": [
            "ComponentPerModeResult"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4991": [
            "DesignEntityModalAnalysisGroupResults"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4992": [
            "ModalCMSResultsForModeAndFE"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4993": [
            "PerModeResultsReport"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4994": [
            "RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4995": [
            "RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4996": [
            "RigidlyConnectedDesignEntityGroupModalAnalysis"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4997": [
            "ShaftPerModeResult"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4998": [
            "SingleExcitationResultsModalAnalysis"
        ],
        "_private.system_model.analyses_and_results.modal_analyses.reporting._4999": [
            "SingleModeResults"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CalculateFullFEResultsForMode",
    "CampbellDiagramReport",
    "ComponentPerModeResult",
    "DesignEntityModalAnalysisGroupResults",
    "ModalCMSResultsForModeAndFE",
    "PerModeResultsReport",
    "RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis",
    "RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis",
    "RigidlyConnectedDesignEntityGroupModalAnalysis",
    "ShaftPerModeResult",
    "SingleExcitationResultsModalAnalysis",
    "SingleModeResults",
)
