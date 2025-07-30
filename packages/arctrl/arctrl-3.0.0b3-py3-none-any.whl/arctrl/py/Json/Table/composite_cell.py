from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.list import (singleton, of_array, FSharpList)
from ...fable_modules.fable_library.seq import map
from ...fable_modules.fable_library.string_ import (to_fail, printf)
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import (to_enumerable, IEnumerable_1)
from ...fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, index, IGetters)
from ...fable_modules.thoth_json_core.encode import list_1
from ...fable_modules.thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ...Core.data import Data
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Table.composite_cell import CompositeCell
from ..data import (encoder as encoder_1, decoder as decoder_5, compressed_encoder, compressed_decoder)
from ..ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder)
from ..string_table import (encode_string, decode_string)
from .oatable import (encode_oa, decode_oa)

__A_ = TypeVar("__A_")

def encoder(cc: CompositeCell) -> IEncodable:
    def oa_to_json_string(oa: OntologyAnnotation, cc: Any=cc) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    class ObjectExpr2779(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], cc: Any=cc) -> Any:
            return helpers_1.encode_string(cc.fields[0])

    class ObjectExpr2780(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any], cc: Any=cc) -> Any:
            return helpers.encode_string(cc.fields[0])

    pattern_input: tuple[str, FSharpList[IEncodable]] = (("Term", singleton(oa_to_json_string(cc.fields[0])))) if (cc.tag == 0) else ((("Unitized", of_array([ObjectExpr2779(), oa_to_json_string(cc.fields[1])]))) if (cc.tag == 2) else ((("Data", singleton(encoder_1(cc.fields[0])))) if (cc.tag == 3) else (("FreeText", singleton(ObjectExpr2780())))))
    class ObjectExpr2781(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], cc: Any=cc) -> Any:
            return helpers_2.encode_string(pattern_input[0])

    values_1: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("celltype", ObjectExpr2781()), ("values", list_1(pattern_input[1]))])
    class ObjectExpr2782(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], cc: Any=cc) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values_1)
            return helpers_3.encode_object(arg)

    return ObjectExpr2782()


def _arrow2788(get: IGetters) -> CompositeCell:
    match_value: str
    object_arg: IRequiredGetter = get.Required
    match_value = object_arg.Field("celltype", string)
    def _arrow2783(__unit: None=None) -> str:
        arg_3: Decoder_1[str] = index(0, string)
        object_arg_1: IRequiredGetter = get.Required
        return object_arg_1.Field("values", arg_3)

    def _arrow2784(__unit: None=None) -> OntologyAnnotation:
        arg_5: Decoder_1[OntologyAnnotation] = index(0, OntologyAnnotation_decoder)
        object_arg_2: IRequiredGetter = get.Required
        return object_arg_2.Field("values", arg_5)

    def _arrow2785(__unit: None=None) -> str:
        arg_7: Decoder_1[str] = index(0, string)
        object_arg_3: IRequiredGetter = get.Required
        return object_arg_3.Field("values", arg_7)

    def _arrow2786(__unit: None=None) -> OntologyAnnotation:
        arg_9: Decoder_1[OntologyAnnotation] = index(1, OntologyAnnotation_decoder)
        object_arg_4: IRequiredGetter = get.Required
        return object_arg_4.Field("values", arg_9)

    def _arrow2787(__unit: None=None) -> Data:
        arg_11: Decoder_1[Data] = index(0, decoder_5)
        object_arg_5: IRequiredGetter = get.Required
        return object_arg_5.Field("values", arg_11)

    return CompositeCell(1, _arrow2783()) if (match_value == "FreeText") else (CompositeCell(0, _arrow2784()) if (match_value == "Term") else (CompositeCell(2, _arrow2785(), _arrow2786()) if (match_value == "Unitized") else (CompositeCell(3, _arrow2787()) if (match_value == "Data") else to_fail(printf("Error reading CompositeCell from json string: %A"))(match_value))))


decoder: Decoder_1[CompositeCell] = object(_arrow2788)

def encoder_compressed(string_table: Any, oa_table: Any, cc: CompositeCell) -> IEncodable:
    pattern_input: tuple[str, FSharpList[IEncodable]] = (("Term", singleton(encode_oa(oa_table, cc.fields[0])))) if (cc.tag == 0) else ((("Unitized", of_array([encode_string(string_table, cc.fields[0]), encode_oa(oa_table, cc.fields[1])]))) if (cc.tag == 2) else ((("Data", singleton(compressed_encoder(string_table, cc.fields[0])))) if (cc.tag == 3) else (("FreeText", singleton(encode_string(string_table, cc.fields[0]))))))
    values_1: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("t", encode_string(string_table, pattern_input[0])), ("v", list_1(pattern_input[1]))])
    class ObjectExpr2789(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cc: Any=cc) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values_1)
            return helpers.encode_object(arg)

    return ObjectExpr2789()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation]) -> Decoder_1[CompositeCell]:
    def _arrow2795(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table) -> CompositeCell:
        match_value: str
        arg_1: Decoder_1[str] = decode_string(string_table)
        object_arg: IRequiredGetter = get.Required
        match_value = object_arg.Field("t", arg_1)
        def _arrow2790(__unit: None=None) -> str:
            arg_3: Decoder_1[str] = index(0, decode_string(string_table))
            object_arg_1: IRequiredGetter = get.Required
            return object_arg_1.Field("v", arg_3)

        def _arrow2791(__unit: None=None) -> OntologyAnnotation:
            arg_5: Decoder_1[OntologyAnnotation] = index(0, decode_oa(oa_table))
            object_arg_2: IRequiredGetter = get.Required
            return object_arg_2.Field("v", arg_5)

        def _arrow2792(__unit: None=None) -> str:
            arg_7: Decoder_1[str] = index(0, decode_string(string_table))
            object_arg_3: IRequiredGetter = get.Required
            return object_arg_3.Field("v", arg_7)

        def _arrow2793(__unit: None=None) -> OntologyAnnotation:
            arg_9: Decoder_1[OntologyAnnotation] = index(1, decode_oa(oa_table))
            object_arg_4: IRequiredGetter = get.Required
            return object_arg_4.Field("v", arg_9)

        def _arrow2794(__unit: None=None) -> Data:
            arg_11: Decoder_1[Data] = index(0, compressed_decoder(string_table))
            object_arg_5: IRequiredGetter = get.Required
            return object_arg_5.Field("v", arg_11)

        return CompositeCell(1, _arrow2790()) if (match_value == "FreeText") else (CompositeCell(0, _arrow2791()) if (match_value == "Term") else (CompositeCell(2, _arrow2792(), _arrow2793()) if (match_value == "Unitized") else (CompositeCell(3, _arrow2794()) if (match_value == "Data") else to_fail(printf("Error reading CompositeCell from json string: %A"))(match_value))))

    return object(_arrow2795)


__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed"]

