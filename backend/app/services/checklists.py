"""Structured checklist rules transcribed from the TTB PDF guidance."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import BeverageType, RequirementLevel


@dataclass(frozen=True)
class ChecklistRule:
    """A transcribed TTB checklist rule used at runtime."""

    id: str
    label: str
    section: str
    requirement_level: RequirementLevel
    evaluation_type: str


CHECKLISTS: dict[BeverageType, list[ChecklistRule]] = {
    BeverageType.WINE: [
        ChecklistRule("brand_name", "Brand Name", "Brand Label", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("designation", "Class / Type Designation", "Brand Label", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule(
            "appellation_of_origin",
            "Appellation of Origin",
            "Brand Label",
            RequirementLevel.CONDITIONAL,
            "conditional_appellation",
        ),
        ChecklistRule("alcohol_content", "Alcohol Content", "Any Label", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("net_contents", "Net Contents", "Any Label", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("name_and_address", "Name and Address", "Any Label", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule(
            "sulfite_declaration",
            "Sulfite Declaration",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "government_warning",
            "Government Warning Statement",
            "Any Label",
            RequirementLevel.REQUIRED,
            "exact_warning",
        ),
        ChecklistRule(
            "country_of_origin",
            "Country of Origin",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_import",
        ),
        ChecklistRule(
            "yellow_5_declaration",
            "FD&C Yellow #5 Disclosure",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "cochineal_or_carmine_declaration",
            "Cochineal Extract / Carmine Disclosure",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
    ],
    BeverageType.DISTILLED_SPIRITS: [
        ChecklistRule(
            "same_field_of_vision",
            "Same Field of Vision",
            "Same Field of Vision",
            RequirementLevel.REQUIRED,
            "layout_review",
        ),
        ChecklistRule("brand_name", "Brand Name", "Same Field of Vision", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("designation", "Class / Type Designation", "Same Field of Vision", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("alcohol_content", "Alcohol Content", "Same Field of Vision", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("net_contents", "Net Contents", "Any Label", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("name_and_address", "Name and Address", "Any Label", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule(
            "government_warning",
            "Government Warning Statement",
            "Any Label",
            RequirementLevel.REQUIRED,
            "exact_warning",
        ),
        ChecklistRule(
            "country_of_origin",
            "Country of Origin",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_import",
        ),
        ChecklistRule(
            "sulfite_declaration",
            "Sulfite Declaration",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "coloring_statement",
            "Coloring Material Disclosure",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "yellow_5_declaration",
            "FD&C Yellow #5 Disclosure",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "cochineal_or_carmine_declaration",
            "Cochineal Extract / Carmine Disclosure",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "treatment_with_wood_statement",
            "Treatment with Wood Statement",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "commodity_statement",
            "Commodity Statement",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "state_of_distillation",
            "State of Distillation",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "age_statement",
            "Statement of Age",
            "Any Label",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
    ],
    BeverageType.MALT_BEVERAGE: [
        ChecklistRule("brand_name", "Brand Name", "Mandatory Information", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("designation", "Designation", "Mandatory Information", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("name_and_address", "Name and Address", "Mandatory Information", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule("net_contents", "Net Contents", "Mandatory Information", RequirementLevel.REQUIRED, "text_presence"),
        ChecklistRule(
            "alcohol_content",
            "Alcohol Content",
            "Mandatory Information",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "government_warning",
            "Government Warning Statement",
            "Mandatory Information",
            RequirementLevel.REQUIRED,
            "exact_warning",
        ),
        ChecklistRule(
            "country_of_origin",
            "Country of Origin",
            "Mandatory Information",
            RequirementLevel.CONDITIONAL,
            "conditional_import",
        ),
        ChecklistRule(
            "importer_name_and_address",
            "Importer Name and Address",
            "Mandatory Information",
            RequirementLevel.CONDITIONAL,
            "conditional_import",
        ),
        ChecklistRule(
            "yellow_5_declaration",
            "FD&C Yellow #5 Disclosure",
            "Mandatory Information",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "cochineal_or_carmine_declaration",
            "Cochineal Extract / Carmine Disclosure",
            "Mandatory Information",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "sulfite_declaration",
            "Sulfite Declaration",
            "Mandatory Information",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
        ChecklistRule(
            "aspartame_declaration",
            "Aspartame Declaration",
            "Mandatory Information",
            RequirementLevel.CONDITIONAL,
            "conditional_disclosure",
        ),
    ],
}
