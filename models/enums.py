from sqlalchemy import Enum as SAEnum


SexEnum = SAEnum("male", "female", "other", name="sex_enum")
ModalityEnum = SAEnum("lab", "instrumental", "other", name="exam_modality_enum")
FileKindEnum = SAEnum("image", "pdf", "dicom", "other", name="file_kind_enum")
