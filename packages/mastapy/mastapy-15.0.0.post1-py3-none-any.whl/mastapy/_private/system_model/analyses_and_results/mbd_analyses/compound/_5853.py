"""CouplingCompoundMultibodyDynamicsAnalysis"""

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
    _5916,
)

_COUPLING_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound",
    "CouplingCompoundMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2892
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7882,
        _7885,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5701
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
        _5816,
        _5837,
        _5842,
        _5897,
        _5898,
        _5920,
        _5935,
    )

    Self = TypeVar("Self", bound="CouplingCompoundMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingCompoundMultibodyDynamicsAnalysis._Cast_CouplingCompoundMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingCompoundMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingCompoundMultibodyDynamicsAnalysis:
    """Special nested class for casting CouplingCompoundMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "CouplingCompoundMultibodyDynamicsAnalysis"

    @property
    def specialised_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5916.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis":
        return self.__parent__._cast(
            _5916.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis
        )

    @property
    def abstract_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5816.AbstractAssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5816,
        )

        return self.__parent__._cast(
            _5816.AbstractAssemblyCompoundMultibodyDynamicsAnalysis
        )

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
    def clutch_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5837.ClutchCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5837,
        )

        return self.__parent__._cast(_5837.ClutchCompoundMultibodyDynamicsAnalysis)

    @property
    def concept_coupling_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5842.ConceptCouplingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5842,
        )

        return self.__parent__._cast(
            _5842.ConceptCouplingCompoundMultibodyDynamicsAnalysis
        )

    @property
    def part_to_part_shear_coupling_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5898.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5898,
        )

        return self.__parent__._cast(
            _5898.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spring_damper_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5920.SpringDamperCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5920,
        )

        return self.__parent__._cast(
            _5920.SpringDamperCompoundMultibodyDynamicsAnalysis
        )

    @property
    def torque_converter_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5935.TorqueConverterCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5935,
        )

        return self.__parent__._cast(
            _5935.TorqueConverterCompoundMultibodyDynamicsAnalysis
        )

    @property
    def coupling_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "CouplingCompoundMultibodyDynamicsAnalysis":
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
class CouplingCompoundMultibodyDynamicsAnalysis(
    _5916.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis
):
    """CouplingCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_5701.CouplingMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.CouplingMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5701.CouplingMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.CouplingMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingCompoundMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CouplingCompoundMultibodyDynamicsAnalysis
        """
        return _Cast_CouplingCompoundMultibodyDynamicsAnalysis(self)
