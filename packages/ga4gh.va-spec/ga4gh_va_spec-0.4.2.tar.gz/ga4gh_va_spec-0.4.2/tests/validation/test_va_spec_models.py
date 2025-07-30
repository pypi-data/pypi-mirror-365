"""Test VA Spec Pydantic model"""

import json
from copy import deepcopy

import pytest
import yaml
from ga4gh.core.models import Coding, MappableConcept, code, iriReference
from ga4gh.va_spec import acmg_2015, base, ccv_2022
from ga4gh.va_spec.aac_2017.models import VariantTherapeuticResponseStudyStatement
from ga4gh.va_spec.acmg_2015.models import (
    VariantPathogenicityEvidenceLine,
    VariantPathogenicityStatement,
)
from ga4gh.va_spec.base import (
    Agent,
    CohortAlleleFrequencyStudyResult,
    ExperimentalVariantFunctionalImpactStudyResult,
)
from ga4gh.va_spec.base.core import EvidenceLine, Method, StudyGroup, StudyResult
from ga4gh.va_spec.base.domain_entities import ConditionSet
from ga4gh.va_spec.ccv_2022.models import (
    VariantOncogenicityEvidenceLine,
    VariantOncogenicityStudyStatement,
)
from pydantic import ValidationError

from tests.conftest import SUBMODULES_DIR

VA_SPEC_TESTS_DIR = SUBMODULES_DIR / "tests"
VA_SPEC_TEST_FIXTURES = VA_SPEC_TESTS_DIR / "fixtures"


@pytest.fixture(scope="module")
def test_definitions():
    """Create test fixture for VA Spec test definitions"""
    with (VA_SPEC_TESTS_DIR / "test_definitions.yaml").open() as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def caf():
    """Create test fixture for CohortAlleleFrequencyStudyResult"""
    return CohortAlleleFrequencyStudyResult(
        focusAllele="allele.json#/1",
        focusAlleleCount=0,
        focusAlleleFrequency=0,
        locusAlleleCount=34086,
        cohort=StudyGroup(id="ALL", name="Overall"),
    )


def test_condition_set():
    """Ensure ConditionSet model works as expected"""
    condition_set_dict = {
        "membershipOperator": "AND",
        "conditions": [
            {
                "conceptType": "Disease",
                "id": "civic.did:3387",
                "mappings": [
                    {
                        "coding": {
                            "code": "DOID:0081279",
                            "system": "https://disease-ontology.org/?id=",
                        },
                        "relation": "exactMatch",
                    }
                ],
                "name": "Diffuse Astrocytoma, MYB- Or MYBL1-altered",
            },
            {
                "conditions": [
                    {
                        "conceptType": "Phenotype",
                        "id": "civic.phenotype:8121",
                        "mappings": [
                            {
                                "coding": {
                                    "code": "HP:0011463",
                                    "system": "https://hpo.jax.org/browse/term/",
                                },
                                "relation": "exactMatch",
                            }
                        ],
                        "name": "Childhood onset",
                    },
                    {
                        "conceptType": "Phenotype",
                        "id": "civic.phenotype:2656",
                        "mappings": [
                            {
                                "coding": {
                                    "code": "HP:0003621",
                                    "id": "HP:0003621",
                                    "system": "https://hpo.jax.org/browse/term/",
                                },
                                "relation": "exactMatch",
                            }
                        ],
                        "name": "Juvenile onset",
                    },
                    {
                        "conceptType": "Phenotype",
                        "id": "civic.phenotype:2643",
                        "mappings": [
                            {
                                "coding": {
                                    "code": "HP:0003581",
                                    "system": "https://hpo.jax.org/browse/term/",
                                },
                                "relation": "exactMatch",
                            }
                        ],
                        "name": "Adult onset",
                    },
                ],
                "membershipOperator": "OR",
            },
        ],
    }
    assert ConditionSet(**condition_set_dict)

    invalid_params = deepcopy(condition_set_dict)
    invalid_params["conditions"].pop()

    with pytest.raises(
        ValidationError, match="List should have at least 2 items after validation"
    ):
        ConditionSet(**invalid_params)


def test_agent():
    """Ensure Agent model works as expected"""
    agent = Agent(name="Joe")
    assert agent.type == "Agent"
    assert agent.name == "Joe"

    with pytest.raises(AttributeError, match="'Agent' object has no attribute 'label'"):
        agent.label  # noqa: B018

    with pytest.raises(ValueError, match='"Agent" object has no field "label"'):
        agent.label = "This is an agent"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Agent(name="Joe", label="Jane")


def test_caf_study_result(caf):
    """Ensure CohortAlleleFrequencyStudyResult model works as expected"""
    assert caf.focusAllele.root == "allele.json#/1"
    assert caf.focusAlleleCount == 0
    assert caf.focusAlleleFrequency == 0
    assert caf.locusAlleleCount == 34086
    assert caf.cohort.id == "ALL"
    assert caf.cohort.name == "Overall"
    assert caf.cohort.type == "StudyGroup"

    assert "focus" not in caf.model_dump()
    assert "focus" not in json.loads(caf.model_dump_json())

    with pytest.raises(
        AttributeError,
        match="'CohortAlleleFrequencyStudyResult' object has no attribute 'focus'",
    ):
        caf.focus  # noqa: B018

    with pytest.raises(
        ValueError,
        match='"CohortAlleleFrequencyStudyResult" object has no field "focus"',
    ):
        caf.focus = "focus"


def test_experimental_func_impact_study_result():
    """Ensure ExperimentalVariantFunctionalImpactStudyResult model works as expected"""
    experimental_func_impact_study_result = (
        ExperimentalVariantFunctionalImpactStudyResult(focusVariant="allele.json#/1")
    )
    assert experimental_func_impact_study_result.focusVariant.root == "allele.json#/1"

    assert "focus" not in experimental_func_impact_study_result.model_dump()
    assert "focus" not in json.loads(
        experimental_func_impact_study_result.model_dump_json()
    )

    with pytest.raises(
        AttributeError,
        match="'ExperimentalVariantFunctionalImpactStudyResult' object has no attribute 'focus'",
    ):
        experimental_func_impact_study_result.focus  # noqa: B018

    with pytest.raises(
        ValueError,
        match='"ExperimentalVariantFunctionalImpactStudyResult" object has no field "focus"',
    ):
        experimental_func_impact_study_result.focus = "focus"


def test_evidence_line(caf):
    """Ensure EvidenceLine model works as expected"""
    el_dict = {
        "type": "EvidenceLine",
        "hasEvidenceItems": [
            iriReference(root="evidence.json#/1"),
            {
                "id": "civic.eid:2997",
                "type": "Statement",
                "proposition": {
                    "type": "VariantTherapeuticResponseProposition",
                    "subjectVariant": {
                        "id": "civic.mpid:33",
                        "type": "CategoricalVariant",
                        "name": "EGFR L858R",
                    },
                    "geneContextQualifier": {
                        "id": "civic.gid:19",
                        "conceptType": "Gene",
                        "name": "EGFR",
                    },
                    "alleleOriginQualifier": {"name": "somatic"},
                    "predicate": "predictsSensitivityTo",
                    "objectTherapeutic": {
                        "id": "civic.tid:146",
                        "conceptType": "Therapy",
                        "name": "Afatinib",
                    },
                    "conditionQualifier": {
                        "id": "civic.did:8",
                        "conceptType": "Disease",
                        "name": "Lung Non-small Cell Carcinoma",
                    },
                },
                "strength": {
                    "primaryCoding": {
                        "system": "AMP/ASCO/CAP (AAC) Guidelines, 2017",
                        "code": "Level A",
                    }
                },
                "classification": {
                    "primaryCoding": {
                        "system": "AMP/ASCO/CAP (AAC) Guidelines, 2017",
                        "code": "Tier I",
                    }
                },
                "specifiedBy": {
                    "id": "civic.method:2019",
                    "name": "CIViC Curation SOP (2019)",
                    "reportedIn": {
                        "name": "Danos et al., 2019, Genome Med.",
                        "title": "Standard operating procedure for curation and clinical interpretation of variants in cancer",
                        "doi": "10.1186/s13073-019-0687-x",
                        "pmid": "31779674",
                        "type": "Document",
                    },
                    "type": "Method",
                },
                "direction": "supports",
            },
        ],
        "directionOfEvidenceProvided": "disputes",
    }
    el = EvidenceLine(**el_dict)
    assert isinstance(el.hasEvidenceItems[0], iriReference)
    assert isinstance(el.hasEvidenceItems[1], VariantTherapeuticResponseStudyStatement)

    el_dict = {
        "type": "EvidenceLine",
        "hasEvidenceItems": [caf.model_dump(exclude_none=True)],
        "directionOfEvidenceProvided": "supports",
    }
    el = EvidenceLine(**el_dict)
    assert isinstance(el.hasEvidenceItems[0], StudyResult)
    assert isinstance(el.hasEvidenceItems[0].root, CohortAlleleFrequencyStudyResult)

    el_dict = {
        "type": "EvidenceLine",
        "hasEvidenceItems": [
            {"type": "EvidenceLine", "directionOfEvidenceProvided": "neutral"}
        ],
        "directionOfEvidenceProvided": "supports",
    }
    el = EvidenceLine(**el_dict)
    assert isinstance(el.hasEvidenceItems[0], EvidenceLine)

    el_dict = {
        "type": "EvidenceLine",
        "hasEvidenceItems": ["evidence_items.json#/1"],
        "directionOfEvidenceProvided": "supports",
    }
    el = EvidenceLine(**el_dict)
    assert isinstance(el.hasEvidenceItems[0], iriReference)

    el_dict = {
        "type": "EvidenceLine",
        "hasEvidenceItems": None,
        "directionOfEvidenceProvided": "supports",
    }
    assert EvidenceLine(**el_dict)

    invalid_params = {
        "type": "EvidenceLine",
        "hasEvidenceItems": [Agent(name="Joe")],
        "directionOfEvidenceProvided": "supports",
    }
    with pytest.raises(
        ValueError, match="Unable to find valid model for `hasEvidenceItems`"
    ):
        EvidenceLine(**invalid_params)

    invalid_params = {
        "type": "EvidenceLine",
        "hasEvidenceItems": [{"type": "Statement"}],
        "directionOfEvidenceProvided": "supports",
    }
    with pytest.raises(
        ValueError, match="Unable to find valid model for `hasEvidenceItems`"
    ):
        EvidenceLine(**invalid_params)


def test_variant_pathogenicity_stmt():
    """Ensure VariantPathogenicityStatement model works as expected"""
    params = {
        "direction": "supports",
        "proposition": {
            "type": "VariantPathogenicityProposition",
            "predicate": "isCausalFor",
            "objectCondition": "conditions.json#/1",
            "subjectVariant": "alleles.json#/1",
        },
        "classification": {
            "primaryCoding": {"code": "pathogenic", "system": "ACMG Guidelines, 2015"}
        },
        "specifiedBy": {
            "reportedIn": {
                "type": "Document",
                "pmid": "25741868",
                "name": "ACMG Guidelines, 2015",
            }
        },
    }
    assert VariantPathogenicityStatement(**params)

    invalid_params = deepcopy(params)
    del invalid_params["classification"]["primaryCoding"]
    invalid_params["classification"]["name"] = "test"
    with pytest.raises(ValueError, match="`primaryCoding` is required."):
        VariantPathogenicityStatement(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["classification"]["primaryCoding"]["system"] = (
        "AMP/ASCO/CAP (AAC) Guidelines, 2017"
    )
    with pytest.raises(ValueError, match="`primaryCoding.system` must be one of"):
        VariantPathogenicityStatement(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["classification"]["primaryCoding"]["code"] = (
        "pathogenic, low penetrance"
    )
    with pytest.raises(ValueError, match="`primaryCoding.code` must be one of"):
        VariantPathogenicityStatement(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["classification"]["primaryCoding"]["system"] = (
        "ClinGen Low Penetrance and Risk Allele Recommendations, 2024"
    )
    invalid_params["classification"]["primaryCoding"]["code"] = "pathogenic"
    with pytest.raises(ValueError, match="`primaryCoding.code` must be one of"):
        VariantPathogenicityStatement(**invalid_params)

    invalid_params = deepcopy(params)
    del invalid_params["proposition"]  # proposition is required for statement
    with pytest.raises(ValueError, match="Field required"):
        VariantPathogenicityStatement(**invalid_params)


def test_variant_pathogenicity_el():
    """Ensure VariantPathogenicityEvidenceLine model works as expected"""
    params = {
        "type": "EvidenceLine",
        "specifiedBy": {
            "type": "Method",
            "id": "PS3",
            "name": "ACMG 2015 PS3 Criterion",
            "reportedIn": {
                "type": "Document",
                "pmid": "25741868",
                "name": "ACMG Guidelines, 2015",
            },
            "methodType": "PS3",
        },
        "directionOfEvidenceProvided": "supports",
        "evidenceOutcome": {
            "primaryCoding": {
                "code": "PS3_supporting",
                "system": "ACMG Guidelines, 2015",
            },
            "name": "ACMG 2015 PS3 Supporting Criterion Met",
        },
        "strengthOfEvidenceProvided": {
            "primaryCoding": {
                "system": "ACMG Guidelines, 2015",
                "code": "supporting",
            }
        },
    }
    vp = VariantPathogenicityEvidenceLine(**params)

    assert isinstance(vp.specifiedBy, Method)
    assert vp.evidenceOutcome == MappableConcept(
        primaryCoding=Coding(
            code=code(root="PS3_supporting"), system="ACMG Guidelines, 2015"
        ),
        name="ACMG 2015 PS3 Supporting Criterion Met",
    )

    invalid_params = deepcopy(params)
    invalid_params["evidenceOutcome"]["primaryCoding"]["code"] = "PS3 supporting"
    with pytest.raises(
        ValueError,
        match="`primaryCoding.code` does not match regex pattern",
    ):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["strengthOfEvidenceProvided"] = None
    with pytest.raises(
        ValueError,
        match="`strengthOfEvidenceProvided` is required when `directionOfEvidenceProvided` is 'supports' or 'disputes'.",
    ):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["strengthOfEvidenceProvided"]["primaryCoding"]["code"] = "definitive"
    with pytest.raises(ValueError, match="`primaryCoding.code` must be one of"):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    del invalid_params["specifiedBy"]["reportedIn"]
    with pytest.raises(ValueError, match="`reportedIn` is required"):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    del invalid_params[
        "directionOfEvidenceProvided"
    ]  # directionOfEvidenceProvided is required for statement
    with pytest.raises(ValueError, match="Field required"):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["strengthOfEvidenceProvided"] = {"name": "test"}
    with pytest.raises(ValueError, match="`primaryCoding` is required."):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["strengthOfEvidenceProvided"] = {
        "primaryCoding": {
            "system": "AMP/ASCO/CAP (AAC) Guidelines, 2017",
            "code": "strong",
        }
    }
    with pytest.raises(ValueError, match="`primaryCoding.system` must be"):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["strengthOfEvidenceProvided"] = {
        "primaryCoding": {"system": "ACMG Guidelines, 2015", "code": "PS3"}
    }
    with pytest.raises(ValueError, match="`primaryCoding.code` must be"):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["specifiedBy"]["methodType"] = "OS1"
    with pytest.raises(
        ValueError,
        match="'OS1' is not a valid VariantPathogenicityEvidenceLine.Criterion",
    ):
        VariantPathogenicityEvidenceLine(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["directionOfEvidenceProvided"] = "neutral"
    with pytest.raises(
        ValueError,
        match="`strengthOfEvidenceProvided` is not allowed when `directionOfEvidenceProvided` is 'neutral'.",
    ):
        VariantPathogenicityEvidenceLine(**invalid_params)


def test_variant_onco_stmt():
    """Ensure VariantOncogenicityStudyStatement model works as expected"""
    params = {
        "direction": "neutral",
        "proposition": {
            "type": "VariantOncogenicityProposition",
            "predicate": "isOncogenicFor",
            "objectTumorType": "conditions.json#/1",
            "subjectVariant": "alleles.json#/1",
        },
        "classification": {
            "primaryCoding": {
                "code": "oncogenic",
                "system": "ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022",
            }
        },
        "specifiedBy": "documents.json#/1",
        "strength": {
            "primaryCoding": {
                "code": "definitive",
                "system": "ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022",
            }
        },
    }
    assert VariantOncogenicityStudyStatement(**params)

    valid_params = deepcopy(params)
    valid_params["strength"] = None
    assert VariantOncogenicityStudyStatement(**valid_params)

    invalid_params = deepcopy(params)
    invalid_params["strength"]["primaryCoding"]["code"] = "oncogenic"
    with pytest.raises(ValueError, match="`primaryCoding.code` must be one of"):
        VariantOncogenicityStudyStatement(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["strength"]["primaryCoding"]["system"] = "ACMG Guidelines, 2015"
    with pytest.raises(ValueError, match="`primaryCoding.system` must be"):
        VariantOncogenicityStudyStatement(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["classification"]["primaryCoding"]["code"] = "pathogenic"
    with pytest.raises(ValueError, match="`primaryCoding.code` must be one of"):
        VariantOncogenicityStudyStatement(**invalid_params)

    invalid_params = deepcopy(params)
    invalid_params["classification"]["primaryCoding"]["system"] = (
        "ACMG Guidelines, 2015"
    )
    with pytest.raises(ValueError, match="`primaryCoding.system` must be"):
        VariantOncogenicityStudyStatement(**invalid_params)


def test_variant_onco_el():
    """Ensure VariantOncogenicityEvidenceLine model works as expected"""
    vo = VariantOncogenicityEvidenceLine(
        type="EvidenceLine",
        specifiedBy={
            "type": "Method",
            "reportedIn": {
                "type": "Document",
                "pmid": "35101336",
                "name": "ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022",
            },
            "methodType": "OS2",
        },
        directionOfEvidenceProvided="supports",
        scoreOfEvidenceProvided=1,
        evidenceOutcome={
            "primaryCoding": {
                "code": "OS2_supporting",
                "system": "ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022",
            },
        },
        strengthOfEvidenceProvided={
            "primaryCoding": {
                "code": "supporting",
                "system": "ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022",
            }
        },
    )
    assert isinstance(vo.specifiedBy, Method)
    assert vo.evidenceOutcome == MappableConcept(
        primaryCoding=Coding(
            code=code(root="OS2_supporting"),
            system="ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022",
        ),
    )

    vo_invalid_params = vo.model_copy(deep=True).model_dump()
    vo_invalid_params["specifiedBy"]["methodType"] = "PS1"
    with pytest.raises(
        ValueError,
        match="'PS1' is not a valid VariantOncogenicityEvidenceLine.Criterion",
    ):
        VariantOncogenicityEvidenceLine(**vo_invalid_params)

    invalid_params = vo.model_copy(deep=True).model_dump()
    invalid_params["strengthOfEvidenceProvided"]["primaryCoding"]["code"] = "definitive"
    with pytest.raises(ValueError, match="`primaryCoding.code` must be one of"):
        VariantOncogenicityEvidenceLine(**invalid_params)

    invalid_params = vo.model_copy(deep=True).model_dump()
    invalid_params["strengthOfEvidenceProvided"]["primaryCoding"]["system"] = (
        "ACMG Guidelines, 2015"
    )
    with pytest.raises(
        ValueError,
        match="`primaryCoding.system` must be 'ClinGen/CGC/VICC Guidelines for Oncogenicity, 2022'.",
    ):
        VariantOncogenicityEvidenceLine(**invalid_params)

    invalid_params = vo.model_copy(deep=True).model_dump()
    invalid_params["directionOfEvidenceProvided"] = "neutral"
    with pytest.raises(
        ValueError,
        match="`strengthOfEvidenceProvided` is not allowed when `directionOfEvidenceProvided` is 'neutral'.",
    ):
        VariantOncogenicityEvidenceLine(**invalid_params)


def test_examples(test_definitions):
    """Test VA Spec examples"""
    va_spec_schema_mapping = {
        "va-spec.base": base,
        "va-spec.acmg-2015": acmg_2015,
        "va-spec.ccv-2022": ccv_2022,
    }

    for test in test_definitions["tests"]:
        with (VA_SPEC_TEST_FIXTURES / test["test_file"]).open() as f:
            data = yaml.safe_load(f)

        ns = test["namespace"]
        pydantic_models = va_spec_schema_mapping.get(ns)
        if not pydantic_models:
            continue

        schema_model = test["definition"]
        if schema_model == "Statement":
            continue

        pydantic_model = getattr(pydantic_models, schema_model, False)
        assert pydantic_model, schema_model

        try:
            assert pydantic_model(**data)
        except ValidationError as e:
            err_msg = f"ValidationError in {test['test_file']}: {e}"
            raise AssertionError(err_msg)  # noqa: B904
