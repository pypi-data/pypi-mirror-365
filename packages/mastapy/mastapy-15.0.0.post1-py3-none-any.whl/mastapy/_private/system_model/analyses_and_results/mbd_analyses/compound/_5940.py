"""VirtualComponentCompoundMultibodyDynamicsAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
    _5895,
)

_VIRTUAL_COMPONENT_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound",
    "VirtualComponentCompoundMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2892
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7882,
        _7885,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5801
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
        _5841,
        _5891,
        _5892,
        _5897,
        _5904,
        _5905,
        _5939,
    )

    Self = TypeVar("Self", bound="VirtualComponentCompoundMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="VirtualComponentCompoundMultibodyDynamicsAnalysis._Cast_VirtualComponentCompoundMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentCompoundMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentCompoundMultibodyDynamicsAnalysis:
    """Special nested class for casting VirtualComponentCompoundMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "VirtualComponentCompoundMultibodyDynamicsAnalysis"

    @property
    def mountable_component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5895.MountableComponentCompoundMultibodyDynamicsAnalysis":
        return self.__parent__._cast(
            _5895.MountableComponentCompoundMultibodyDynamicsAnalysis
        )

    @property
    def component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5841.ComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5841,
        )

        return self.__parent__._cast(_5841.ComponentCompoundMultibodyDynamicsAnalysis)

    @property
    def part_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5897.PartCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5897,
        )

        return self.__parent__._cast(_5897.PartCompoundMultibodyDynamicsAnalysis)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7885.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7885,
        )

        return self.__parent__._cast(_7885.PartCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7882.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7882,
        )

        return self.__parent__._cast(_7882.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2892.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2892

        return self.__parent__._cast(_2892.DesignEntityAnalysis)

    @property
    def mass_disc_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5891.MassDiscCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5891,
        )

        return self.__parent__._cast(_5891.MassDiscCompoundMultibodyDynamicsAnalysis)

    @property
    def measurement_component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5892.MeasurementComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5892,
        )

        return self.__parent__._cast(
            _5892.MeasurementComponentCompoundMultibodyDynamicsAnalysis
        )

    @property
    def point_load_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5904.PointLoadCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5904,
        )

        return self.__parent__._cast(_5904.PointLoadCompoundMultibodyDynamicsAnalysis)

    @property
    def power_load_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5905.PowerLoadCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5905,
        )

        return self.__parent__._cast(_5905.PowerLoadCompoundMultibodyDynamicsAnalysis)

    @property
    def unbalanced_mass_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5939.UnbalancedMassCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5939,
        )

        return self.__parent__._cast(
            _5939.UnbalancedMassCompoundMultibodyDynamicsAnalysis
        )

    @property
    def virtual_component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "VirtualComponentCompoundMultibodyDynamicsAnalysis":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class VirtualComponentCompoundMultibodyDynamicsAnalysis(
    _5895.MountableComponentCompoundMultibodyDynamicsAnalysis
):
    """VirtualComponentCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_COMPONENT_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_5801.VirtualComponentMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.VirtualComponentMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5801.VirtualComponentMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.VirtualComponentMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_VirtualComponentCompoundMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentCompoundMultibodyDynamicsAnalysis
        """
        return _Cast_VirtualComponentCompoundMultibodyDynamicsAnalysis(self)
