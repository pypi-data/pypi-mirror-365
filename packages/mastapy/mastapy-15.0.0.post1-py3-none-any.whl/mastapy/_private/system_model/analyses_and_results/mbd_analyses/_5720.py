"""GearMeshMultibodyDynamicsAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5732

_GEAR_MESH_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses",
    "GearMeshMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.nodal_analysis import _72
    from mastapy._private.nodal_analysis.nodal_entities.external_force import _174
    from mastapy._private.system_model.analyses_and_results import _2890, _2892, _2894
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7877,
        _7881,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
        _5662,
        _5672,
        _5677,
        _5691,
        _5694,
        _5697,
        _5709,
        _5715,
        _5725,
        _5733,
        _5736,
        _5739,
        _5775,
        _5782,
        _5785,
        _5803,
        _5806,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2534

    Self = TypeVar("Self", bound="GearMeshMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearMeshMultibodyDynamicsAnalysis._Cast_GearMeshMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshMultibodyDynamicsAnalysis:
    """Special nested class for casting GearMeshMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "GearMeshMultibodyDynamicsAnalysis"

    @property
    def inter_mountable_component_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5732.InterMountableComponentConnectionMultibodyDynamicsAnalysis":
        return self.__parent__._cast(
            _5732.InterMountableComponentConnectionMultibodyDynamicsAnalysis
        )

    @property
    def connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5697.ConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5697,
        )

        return self.__parent__._cast(_5697.ConnectionMultibodyDynamicsAnalysis)

    @property
    def connection_time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "_7881.ConnectionTimeSeriesLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7881,
        )

        return self.__parent__._cast(_7881.ConnectionTimeSeriesLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7877.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7877,
        )

        return self.__parent__._cast(_7877.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2890.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2890

        return self.__parent__._cast(_2890.ConnectionAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2894.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2894

        return self.__parent__._cast(_2894.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2892.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2892

        return self.__parent__._cast(_2892.DesignEntityAnalysis)

    @property
    def agma_gleason_conical_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5662.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5662,
        )

        return self.__parent__._cast(
            _5662.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5672.BevelDifferentialGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5672,
        )

        return self.__parent__._cast(
            _5672.BevelDifferentialGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5677.BevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5677,
        )

        return self.__parent__._cast(_5677.BevelGearMeshMultibodyDynamicsAnalysis)

    @property
    def concept_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5691.ConceptGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5691,
        )

        return self.__parent__._cast(_5691.ConceptGearMeshMultibodyDynamicsAnalysis)

    @property
    def conical_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5694.ConicalGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5694,
        )

        return self.__parent__._cast(_5694.ConicalGearMeshMultibodyDynamicsAnalysis)

    @property
    def cylindrical_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5709.CylindricalGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5709,
        )

        return self.__parent__._cast(_5709.CylindricalGearMeshMultibodyDynamicsAnalysis)

    @property
    def face_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5715.FaceGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5715,
        )

        return self.__parent__._cast(_5715.FaceGearMeshMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5725.HypoidGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5725,
        )

        return self.__parent__._cast(_5725.HypoidGearMeshMultibodyDynamicsAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5733.KlingelnbergCycloPalloidConicalGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5733,
        )

        return self.__parent__._cast(
            _5733.KlingelnbergCycloPalloidConicalGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5736.KlingelnbergCycloPalloidHypoidGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5736,
        )

        return self.__parent__._cast(
            _5736.KlingelnbergCycloPalloidHypoidGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5739.KlingelnbergCycloPalloidSpiralBevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5739,
        )

        return self.__parent__._cast(
            _5739.KlingelnbergCycloPalloidSpiralBevelGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5775.SpiralBevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5775,
        )

        return self.__parent__._cast(_5775.SpiralBevelGearMeshMultibodyDynamicsAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5782.StraightBevelDiffGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5782,
        )

        return self.__parent__._cast(
            _5782.StraightBevelDiffGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5785.StraightBevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5785,
        )

        return self.__parent__._cast(
            _5785.StraightBevelGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def worm_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5803.WormGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5803,
        )

        return self.__parent__._cast(_5803.WormGearMeshMultibodyDynamicsAnalysis)

    @property
    def zerol_bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5806.ZerolBevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5806,
        )

        return self.__parent__._cast(_5806.ZerolBevelGearMeshMultibodyDynamicsAnalysis)

    @property
    def gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "GearMeshMultibodyDynamicsAnalysis":
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
class GearMeshMultibodyDynamicsAnalysis(
    _5732.InterMountableComponentConnectionMultibodyDynamicsAnalysis
):
    """GearMeshMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_MULTIBODY_DYNAMICS_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def average_sliding_velocity_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AverageSlidingVelocityLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def average_sliding_velocity_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AverageSlidingVelocityRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def coefficient_of_friction_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CoefficientOfFrictionLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def coefficient_of_friction_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CoefficientOfFrictionRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def contact_status(self: "Self") -> "_72.GearMeshContactStatus":
        """mastapy.nodal_analysis.GearMeshContactStatus

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ContactStatus")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.NodalAnalysis.GearMeshContactStatus"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.nodal_analysis._72", "GearMeshContactStatus"
        )(value)

    @property
    @exception_bridge
    def equivalent_misalignment_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "EquivalentMisalignmentLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def equivalent_misalignment_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "EquivalentMisalignmentRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def force_normal_to_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ForceNormalToLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def force_normal_to_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ForceNormalToRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def impact_power_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ImpactPowerLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def impact_power_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ImpactPowerRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def impact_power_total(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ImpactPowerTotal")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_time_step(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumTimeStep")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def mesh_power_loss(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshPowerLoss")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def misalignment_due_to_tilt_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MisalignmentDueToTiltLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def misalignment_due_to_tilt_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MisalignmentDueToTiltRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normal_separations_left_flank(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalSeparationsLeftFlank")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def normal_separations_right_flank(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalSeparationsRightFlank")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def normal_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normal_stiffness_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalStiffnessLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normal_stiffness_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalStiffnessRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normal_velocity_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalVelocityLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normal_velocity_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalVelocityRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def pitch_line_velocity_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PitchLineVelocityLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def pitch_line_velocity_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PitchLineVelocityRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def separation(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Separation")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def separation_normal_to_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SeparationNormalToLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def separation_normal_to_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SeparationNormalToRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def separation_transverse_to_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SeparationTransverseToLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def separation_transverse_to_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SeparationTransverseToRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def strain_energy_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StrainEnergyLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def strain_energy_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StrainEnergyRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def strain_energy_total(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StrainEnergyTotal")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TiltStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tooth_passing_frequency(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ToothPassingFrequency")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tooth_passing_speed_gear_a(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ToothPassingSpeedGearA")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tooth_passing_speed_gear_b(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ToothPassingSpeedGearB")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def transverse_stiffness_left_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TransverseStiffnessLeftFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def transverse_stiffness_right_flank(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TransverseStiffnessRightFlank")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2534.GearMesh":
        """mastapy.system_model.connections_and_sockets.gears.GearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gear_mesh_contacts(self: "Self") -> "_174.GearMeshBothFlankContacts":
        """mastapy.nodal_analysis.nodal_entities.external_force.GearMeshBothFlankContacts

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearMeshContacts")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearMeshMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearMeshMultibodyDynamicsAnalysis
        """
        return _Cast_GearMeshMultibodyDynamicsAnalysis(self)
