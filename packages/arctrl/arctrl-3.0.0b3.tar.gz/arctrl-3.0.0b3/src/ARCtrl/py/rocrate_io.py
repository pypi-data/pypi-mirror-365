from __future__ import annotations
from typing import Any
from .Core.arc_types import ArcInvestigation
from .Core.Helper.collections_ import ResizeArray_choose
from .FileSystem.file_system import FileSystem
from .Json.ROCrate.ldgraph import (encoder, decoder)
from .Json.ROCrate.ldnode import decoder as decoder_1
from .ROCrate.Generic.dataset import LDDataset
from .ROCrate.Generic.file import LDFile
from .ROCrate.ldcontext import LDContext
from .ROCrate.ldobject import (LDNode, LDRef, LDGraph)
from .ROCrate.rocrate_context import (init_v1_1, init_bioschemas_context)
from .conversion import (ARCtrl_ArcInvestigation__ArcInvestigation_ToROCrateInvestigation_1695DD5C, ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8)
from .fable_modules.fable_library.date import now
from .fable_modules.fable_library.option import value as value_2
from .fable_modules.fable_library.reflection import (TypeInfo, class_type)
from .fable_modules.fable_library.seq import exactly_one
from .fable_modules.fable_library.types import Array
from .fable_modules.thoth_json_core.decode import map
from .fable_modules.thoth_json_core.types import (IEncodable, Decoder_1)

def _expr3603() -> TypeInfo:
    return class_type("ARCtrl.Json.ARC.ROCrate", None, ROCrate)


class ROCrate:
    ...

ROCrate_reflection = _expr3603

def ROCrate_getDefaultLicense(__unit: None=None) -> str:
    return "ALL RIGHTS RESERVED BY THE AUTHORS"


def ROCrate_get_metadataFileDescriptor(__unit: None=None) -> LDNode:
    node: LDNode = LDNode("ro-crate-metadata.json", ["http://schema.org/CreativeWork"])
    node.SetProperty("http://purl.org/dc/terms/conformsTo", LDRef("https://w3id.org/ro/crate/1.1"))
    node.SetProperty("http://schema.org/about", LDRef("./"))
    return node


def ROCrate_encoder_B568605(isa: ArcInvestigation, license: Any | None=None, fs: FileSystem | None=None) -> IEncodable:
    license_2: Any = ROCrate_getDefaultLicense() if (license is None) else value_2(license)
    isa_1: LDNode = ARCtrl_ArcInvestigation__ArcInvestigation_ToROCrateInvestigation_1695DD5C(isa, fs)
    LDDataset.set_sddate_published_as_date_time(isa_1, now())
    LDDataset.set_license_as_creative_work(isa_1, license_2)
    graph: LDGraph = isa_1.Flatten()
    context: LDContext = LDContext(None, [init_v1_1(), init_bioschemas_context()])
    graph.SetContext(context)
    graph.AddNode(ROCrate_get_metadataFileDescriptor())
    graph.Compact_InPlace()
    return encoder(graph)


def ROCrate_get_decoder(__unit: None=None) -> Decoder_1[tuple[ArcInvestigation, Array[str]]]:
    def ctor(graph: LDGraph) -> tuple[ArcInvestigation, Array[str]]:
        match_value: LDNode | None = graph.TryGetNode("./")
        if match_value is None:
            raise Exception("RO-Crate graph did not contain root data Entity")

        else: 
            node: LDNode = match_value
            def f(n: LDNode, graph: Any=graph) -> str | None:
                if (not n.HasType(LDDataset.schema_type(), graph.TryGetContext())) if ((not (n.Id.find("#") >= 0)) if LDFile.validate(n, graph.TryGetContext()) else False) else False:
                    return n.Id

                else: 
                    return None


            files: Array[str] = ResizeArray_choose(f, graph.Nodes)
            return (ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8(node, graph, graph.TryGetContext()), files)


    return map(ctor, decoder)


def ROCrate_get_decoderDeprecated(__unit: None=None) -> Decoder_1[ArcInvestigation]:
    def ctor(ldnode: LDNode) -> ArcInvestigation:
        return ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8(exactly_one(LDDataset.get_abouts(ldnode)), None, init_v1_1())

    return map(ctor, decoder_1)


__all__ = ["ROCrate_reflection", "ROCrate_getDefaultLicense", "ROCrate_get_metadataFileDescriptor", "ROCrate_encoder_B568605", "ROCrate_get_decoder", "ROCrate_get_decoderDeprecated"]

