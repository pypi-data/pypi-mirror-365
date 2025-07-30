"""ComponentModalAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.modal_analyses import _4934

_COMPONENT_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses",
    "ComponentModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2892, _2894, _2898
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7884,
        _7887,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4843,
        _4844,
        _4847,
        _4850,
        _4854,
        _4856,
        _4857,
        _4859,
        _4862,
        _4864,
        _4869,
        _4872,
        _4875,
        _4878,
        _4881,
        _4885,
        _4888,
        _4891,
        _4893,
        _4894,
        _4898,
        _4900,
        _4902,
        _4906,
        _4908,
        _4910,
        _4914,
        _4917,
        _4920,
        _4922,
        _4923,
        _4925,
        _4930,
        _4932,
        _4936,
        _4940,
        _4941,
        _4942,
        _4943,
        _4944,
        _4948,
        _4950,
        _4951,
        _4956,
        _4959,
        _4962,
        _4965,
        _4967,
        _4968,
        _4969,
        _4971,
        _4972,
        _4975,
        _4976,
        _4977,
        _4978,
        _4983,
        _4986,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2956,
    )
    from mastapy._private.system_model.part_model import _2670

    Self = TypeVar("Self", bound="ComponentModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="ComponentModalAnalysis._Cast_ComponentModalAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentModalAnalysis:
    """Special nested class for casting ComponentModalAnalysis to subclasses."""

    __parent__: "ComponentModalAnalysis"

    @property
    def part_modal_analysis(self: "CastSelf") -> "_4934.PartModalAnalysis":
        return self.__parent__._cast(_4934.PartModalAnalysis)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7887.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7887,
        )

        return self.__parent__._cast(_7887.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7884.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7884,
        )

        return self.__parent__._cast(_7884.PartAnalysisCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2898.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2898

        return self.__parent__._cast(_2898.PartAnalysis)

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
    def abstract_shaft_modal_analysis(
        self: "CastSelf",
    ) -> "_4843.AbstractShaftModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4843,
        )

        return self.__parent__._cast(_4843.AbstractShaftModalAnalysis)

    @property
    def abstract_shaft_or_housing_modal_analysis(
        self: "CastSelf",
    ) -> "_4844.AbstractShaftOrHousingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4844,
        )

        return self.__parent__._cast(_4844.AbstractShaftOrHousingModalAnalysis)

    @property
    def agma_gleason_conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4847.AGMAGleasonConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4847,
        )

        return self.__parent__._cast(_4847.AGMAGleasonConicalGearModalAnalysis)

    @property
    def bearing_modal_analysis(self: "CastSelf") -> "_4850.BearingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4850,
        )

        return self.__parent__._cast(_4850.BearingModalAnalysis)

    @property
    def bevel_differential_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4854.BevelDifferentialGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4854,
        )

        return self.__parent__._cast(_4854.BevelDifferentialGearModalAnalysis)

    @property
    def bevel_differential_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4856.BevelDifferentialPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4856,
        )

        return self.__parent__._cast(_4856.BevelDifferentialPlanetGearModalAnalysis)

    @property
    def bevel_differential_sun_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4857.BevelDifferentialSunGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4857,
        )

        return self.__parent__._cast(_4857.BevelDifferentialSunGearModalAnalysis)

    @property
    def bevel_gear_modal_analysis(self: "CastSelf") -> "_4859.BevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4859,
        )

        return self.__parent__._cast(_4859.BevelGearModalAnalysis)

    @property
    def bolt_modal_analysis(self: "CastSelf") -> "_4862.BoltModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4862,
        )

        return self.__parent__._cast(_4862.BoltModalAnalysis)

    @property
    def clutch_half_modal_analysis(self: "CastSelf") -> "_4864.ClutchHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4864,
        )

        return self.__parent__._cast(_4864.ClutchHalfModalAnalysis)

    @property
    def concept_coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4869.ConceptCouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4869,
        )

        return self.__parent__._cast(_4869.ConceptCouplingHalfModalAnalysis)

    @property
    def concept_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4872.ConceptGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4872,
        )

        return self.__parent__._cast(_4872.ConceptGearModalAnalysis)

    @property
    def conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4875.ConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4875,
        )

        return self.__parent__._cast(_4875.ConicalGearModalAnalysis)

    @property
    def connector_modal_analysis(self: "CastSelf") -> "_4878.ConnectorModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4878,
        )

        return self.__parent__._cast(_4878.ConnectorModalAnalysis)

    @property
    def coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4881.CouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4881,
        )

        return self.__parent__._cast(_4881.CouplingHalfModalAnalysis)

    @property
    def cvt_pulley_modal_analysis(self: "CastSelf") -> "_4885.CVTPulleyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4885,
        )

        return self.__parent__._cast(_4885.CVTPulleyModalAnalysis)

    @property
    def cycloidal_disc_modal_analysis(
        self: "CastSelf",
    ) -> "_4888.CycloidalDiscModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4888,
        )

        return self.__parent__._cast(_4888.CycloidalDiscModalAnalysis)

    @property
    def cylindrical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4891.CylindricalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4891,
        )

        return self.__parent__._cast(_4891.CylindricalGearModalAnalysis)

    @property
    def cylindrical_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4893.CylindricalPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4893,
        )

        return self.__parent__._cast(_4893.CylindricalPlanetGearModalAnalysis)

    @property
    def datum_modal_analysis(self: "CastSelf") -> "_4894.DatumModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4894,
        )

        return self.__parent__._cast(_4894.DatumModalAnalysis)

    @property
    def external_cad_model_modal_analysis(
        self: "CastSelf",
    ) -> "_4898.ExternalCADModelModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4898,
        )

        return self.__parent__._cast(_4898.ExternalCADModelModalAnalysis)

    @property
    def face_gear_modal_analysis(self: "CastSelf") -> "_4900.FaceGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4900,
        )

        return self.__parent__._cast(_4900.FaceGearModalAnalysis)

    @property
    def fe_part_modal_analysis(self: "CastSelf") -> "_4902.FEPartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4902,
        )

        return self.__parent__._cast(_4902.FEPartModalAnalysis)

    @property
    def gear_modal_analysis(self: "CastSelf") -> "_4906.GearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4906,
        )

        return self.__parent__._cast(_4906.GearModalAnalysis)

    @property
    def guide_dxf_model_modal_analysis(
        self: "CastSelf",
    ) -> "_4908.GuideDxfModelModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4908,
        )

        return self.__parent__._cast(_4908.GuideDxfModelModalAnalysis)

    @property
    def hypoid_gear_modal_analysis(self: "CastSelf") -> "_4910.HypoidGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4910,
        )

        return self.__parent__._cast(_4910.HypoidGearModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4914.KlingelnbergCycloPalloidConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4914,
        )

        return self.__parent__._cast(
            _4914.KlingelnbergCycloPalloidConicalGearModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4917.KlingelnbergCycloPalloidHypoidGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4917,
        )

        return self.__parent__._cast(
            _4917.KlingelnbergCycloPalloidHypoidGearModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4920.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4920,
        )

        return self.__parent__._cast(
            _4920.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis
        )

    @property
    def mass_disc_modal_analysis(self: "CastSelf") -> "_4922.MassDiscModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4922,
        )

        return self.__parent__._cast(_4922.MassDiscModalAnalysis)

    @property
    def measurement_component_modal_analysis(
        self: "CastSelf",
    ) -> "_4923.MeasurementComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4923,
        )

        return self.__parent__._cast(_4923.MeasurementComponentModalAnalysis)

    @property
    def microphone_modal_analysis(self: "CastSelf") -> "_4925.MicrophoneModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4925,
        )

        return self.__parent__._cast(_4925.MicrophoneModalAnalysis)

    @property
    def mountable_component_modal_analysis(
        self: "CastSelf",
    ) -> "_4930.MountableComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4930,
        )

        return self.__parent__._cast(_4930.MountableComponentModalAnalysis)

    @property
    def oil_seal_modal_analysis(self: "CastSelf") -> "_4932.OilSealModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4932,
        )

        return self.__parent__._cast(_4932.OilSealModalAnalysis)

    @property
    def part_to_part_shear_coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4936.PartToPartShearCouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4936,
        )

        return self.__parent__._cast(_4936.PartToPartShearCouplingHalfModalAnalysis)

    @property
    def planet_carrier_modal_analysis(
        self: "CastSelf",
    ) -> "_4940.PlanetCarrierModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4940,
        )

        return self.__parent__._cast(_4940.PlanetCarrierModalAnalysis)

    @property
    def point_load_modal_analysis(self: "CastSelf") -> "_4941.PointLoadModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4941,
        )

        return self.__parent__._cast(_4941.PointLoadModalAnalysis)

    @property
    def power_load_modal_analysis(self: "CastSelf") -> "_4942.PowerLoadModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4942,
        )

        return self.__parent__._cast(_4942.PowerLoadModalAnalysis)

    @property
    def pulley_modal_analysis(self: "CastSelf") -> "_4943.PulleyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4943,
        )

        return self.__parent__._cast(_4943.PulleyModalAnalysis)

    @property
    def ring_pins_modal_analysis(self: "CastSelf") -> "_4944.RingPinsModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4944,
        )

        return self.__parent__._cast(_4944.RingPinsModalAnalysis)

    @property
    def rolling_ring_modal_analysis(
        self: "CastSelf",
    ) -> "_4948.RollingRingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4948,
        )

        return self.__parent__._cast(_4948.RollingRingModalAnalysis)

    @property
    def shaft_hub_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4950.ShaftHubConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4950,
        )

        return self.__parent__._cast(_4950.ShaftHubConnectionModalAnalysis)

    @property
    def shaft_modal_analysis(self: "CastSelf") -> "_4951.ShaftModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4951,
        )

        return self.__parent__._cast(_4951.ShaftModalAnalysis)

    @property
    def spiral_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4956.SpiralBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4956,
        )

        return self.__parent__._cast(_4956.SpiralBevelGearModalAnalysis)

    @property
    def spring_damper_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4959.SpringDamperHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4959,
        )

        return self.__parent__._cast(_4959.SpringDamperHalfModalAnalysis)

    @property
    def straight_bevel_diff_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4962.StraightBevelDiffGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4962,
        )

        return self.__parent__._cast(_4962.StraightBevelDiffGearModalAnalysis)

    @property
    def straight_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4965.StraightBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4965,
        )

        return self.__parent__._cast(_4965.StraightBevelGearModalAnalysis)

    @property
    def straight_bevel_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4967.StraightBevelPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4967,
        )

        return self.__parent__._cast(_4967.StraightBevelPlanetGearModalAnalysis)

    @property
    def straight_bevel_sun_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4968.StraightBevelSunGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4968,
        )

        return self.__parent__._cast(_4968.StraightBevelSunGearModalAnalysis)

    @property
    def synchroniser_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4969.SynchroniserHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4969,
        )

        return self.__parent__._cast(_4969.SynchroniserHalfModalAnalysis)

    @property
    def synchroniser_part_modal_analysis(
        self: "CastSelf",
    ) -> "_4971.SynchroniserPartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4971,
        )

        return self.__parent__._cast(_4971.SynchroniserPartModalAnalysis)

    @property
    def synchroniser_sleeve_modal_analysis(
        self: "CastSelf",
    ) -> "_4972.SynchroniserSleeveModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4972,
        )

        return self.__parent__._cast(_4972.SynchroniserSleeveModalAnalysis)

    @property
    def torque_converter_pump_modal_analysis(
        self: "CastSelf",
    ) -> "_4975.TorqueConverterPumpModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4975,
        )

        return self.__parent__._cast(_4975.TorqueConverterPumpModalAnalysis)

    @property
    def torque_converter_turbine_modal_analysis(
        self: "CastSelf",
    ) -> "_4976.TorqueConverterTurbineModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4976,
        )

        return self.__parent__._cast(_4976.TorqueConverterTurbineModalAnalysis)

    @property
    def unbalanced_mass_modal_analysis(
        self: "CastSelf",
    ) -> "_4977.UnbalancedMassModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4977,
        )

        return self.__parent__._cast(_4977.UnbalancedMassModalAnalysis)

    @property
    def virtual_component_modal_analysis(
        self: "CastSelf",
    ) -> "_4978.VirtualComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4978,
        )

        return self.__parent__._cast(_4978.VirtualComponentModalAnalysis)

    @property
    def worm_gear_modal_analysis(self: "CastSelf") -> "_4983.WormGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4983,
        )

        return self.__parent__._cast(_4983.WormGearModalAnalysis)

    @property
    def zerol_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4986.ZerolBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4986,
        )

        return self.__parent__._cast(_4986.ZerolBevelGearModalAnalysis)

    @property
    def component_modal_analysis(self: "CastSelf") -> "ComponentModalAnalysis":
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
class ComponentModalAnalysis(_4934.PartModalAnalysis):
    """ComponentModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2670.Component":
        """mastapy.system_model.part_model.Component

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def system_deflection_results(self: "Self") -> "_2956.ComponentSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.ComponentSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ComponentModalAnalysis
        """
        return _Cast_ComponentModalAnalysis(self)
