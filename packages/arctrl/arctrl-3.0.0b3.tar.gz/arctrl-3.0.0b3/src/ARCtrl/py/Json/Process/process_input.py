from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.list import of_array
from ...fable_modules.thoth_json_core.decode import (one_of, map)
from ...fable_modules.thoth_json_core.types import (IEncodable, Decoder_1)
from ...Core.data import Data
from ...Core.Process.material import Material
from ...Core.Process.process_input import ProcessInput
from ...Core.Process.sample import Sample
from ...Core.Process.source import Source
from ..data import (ROCrate_encoder as ROCrate_encoder_2, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_3)
from .material import (ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_4, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_4)
from .sample import (ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_1, ISAJson_decoder as ISAJson_decoder_2)
from .source import (ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_2, ISAJson_encoder as ISAJson_encoder_4, ISAJson_decoder as ISAJson_decoder_1)

def ROCrate_encoder(value: ProcessInput) -> IEncodable:
    if value.tag == 1:
        return ROCrate_encoder_1(value.fields[0])

    elif value.tag == 2:
        return ROCrate_encoder_2(value.fields[0])

    elif value.tag == 3:
        return ROCrate_encoder_3(value.fields[0])

    else: 
        return ROCrate_encoder_4(value.fields[0])



def _arrow2659(Item: Sample) -> ProcessInput:
    return ProcessInput(1, Item)


def _arrow2662(Item_1: Source) -> ProcessInput:
    return ProcessInput(0, Item_1)


def _arrow2663(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow2664(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ROCrate_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow2659, ROCrate_decoder_1), map(_arrow2662, ROCrate_decoder_2), map(_arrow2663, ROCrate_decoder_3), map(_arrow2664, ROCrate_decoder_4)]))

def ISAJson_encoder(id_map: Any | None, value: ProcessInput) -> IEncodable:
    if value.tag == 1:
        return ISAJson_encoder_1(id_map, value.fields[0])

    elif value.tag == 2:
        return ISAJson_encoder_2(id_map, value.fields[0])

    elif value.tag == 3:
        return ISAJson_encoder_3(id_map, value.fields[0])

    else: 
        return ISAJson_encoder_4(id_map, value.fields[0])



def _arrow2671(Item: Source) -> ProcessInput:
    return ProcessInput(0, Item)


def _arrow2672(Item_1: Sample) -> ProcessInput:
    return ProcessInput(1, Item_1)


def _arrow2673(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow2674(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ISAJson_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow2671, ISAJson_decoder_1), map(_arrow2672, ISAJson_decoder_2), map(_arrow2673, ISAJson_decoder_3), map(_arrow2674, ISAJson_decoder_4)]))

__all__ = ["ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_decoder"]

