from os import PathLike
from pathlib import Path
from typing import Any, cast

from birdnet.acoustic_models.base import AcousticModelBase
from birdnet.acoustic_models.inference.backends import litert_installed, tf_installed
from birdnet.acoustic_models.v2_4.base import AcousticModelBaseV2_4
from birdnet.acoustic_models.v2_4.pb import AcousticPBModelV2_4
from birdnet.acoustic_models.v2_4.tf import AcousticTFModelV2_4
from birdnet.base import ModelBase
from birdnet.geo_models.base import GeoModelBase
from birdnet.geo_models.v2_4.pb import GeoPBModelV2_4
from birdnet.geo_models.v2_4.tf import GeoTFModelV2_4
from birdnet.globals import (
  ACOUSTIC_MODEL_VERSION_V2_4,
  ACOUSTIC_MODEL_VERSIONS,
  GEO_MODEL_VERSION_V2_4,
  GEO_MODEL_VERSIONS,
  LIBRARY_LITERT,
  LIBRARY_TF,
  LIBRARY_TYPES,
  MODEL_BACKEND_PB,
  MODEL_BACKEND_TF,
  MODEL_BACKENDS,
  MODEL_LANGUAGE_EN_US,
  MODEL_LANGUAGES,
  MODEL_PRECISION_FP32,
  MODEL_PRECISIONS,
  MODEL_TYPE_ACOUSTIC,
  MODEL_TYPE_GEO,
  MODEL_TYPES,
  VALID_ACOUSTIC_MODEL_VERSIONS,
  VALID_GEO_MODEL_VERSIONS,
  VALID_LIBRARY_TYPES,
  VALID_MODEL_BACKENDS,
  VALID_MODEL_LANGUAGES,
  VALID_MODEL_PRECISIONS,
  VALID_MODEL_TYPES,
)
from birdnet.helper import check_protobuf_model_files_exist


def _validate_model_type(model_type: Any) -> MODEL_TYPES:  # noqa: ANN401
  if model_type not in VALID_MODEL_TYPES:
    raise ValueError(
      f"Unknown model type: {model_type}. Supported types are: {', '.join(VALID_MODEL_TYPES)}."
    )
  return cast(MODEL_TYPES, model_type)


def _validate_acoustic_model_version(version: Any) -> ACOUSTIC_MODEL_VERSIONS:  # noqa: ANN401
  if version not in VALID_ACOUSTIC_MODEL_VERSIONS:
    raise ValueError(
      f"Unsupported model version: {version}. Available versions are: {', '.join(VALID_ACOUSTIC_MODEL_VERSIONS)}."
    )
  return cast(ACOUSTIC_MODEL_VERSIONS, version)


def _validate_geo_model_version(version: Any) -> GEO_MODEL_VERSIONS:  # noqa: ANN401
  if version not in VALID_GEO_MODEL_VERSIONS:
    raise ValueError(
      f"Unsupported model version: {version}. Available versions are: {', '.join(VALID_GEO_MODEL_VERSIONS)}."
    )
  return cast(GEO_MODEL_VERSIONS, version)


def _validate_backend(backend: Any) -> MODEL_BACKENDS:  # noqa: ANN401
  if backend not in VALID_MODEL_BACKENDS:
    raise ValueError(
      f"Unknown model backend: {backend}. Available backends are: {', '.join(VALID_MODEL_BACKENDS)}."
    )
  return cast(MODEL_BACKENDS, backend)


def _validate_precision(precision: Any) -> MODEL_PRECISIONS:  # noqa: ANN401
  if precision not in VALID_MODEL_PRECISIONS:
    raise ValueError(
      f"Unsupported model precision: {precision}. Currently supported precisions: {', '.join(VALID_MODEL_PRECISIONS)}."
    )
  return cast(MODEL_PRECISIONS, precision)


def _validate_language(lang: Any) -> MODEL_LANGUAGES:  # noqa: ANN401
  if lang not in VALID_MODEL_LANGUAGES:
    raise ValueError(
      f"Language '{lang}' is not supported by the model. Available languages are: {', '.join(VALID_MODEL_LANGUAGES)}."
    )
  return cast(MODEL_LANGUAGES, lang)


def _validate_species_list_path(species_list: Any | PathLike[Any]) -> Path:  # noqa: ANN401
  species_list = Path(species_list)
  if not species_list.is_file():
    raise ValueError(f"Species list file '{species_list.absolute()}' does not exist!")
  return species_list


def _validate_path(path: Any) -> Path:  # noqa: ANN401
  path = Path(path)
  if not path.exists():
    raise ValueError(f"Path '{path.absolute()}' does not exist!")
  return path


def _validate_pb_model_folder(folder_path: Any) -> Path:  # noqa: ANN401
  path = Path(folder_path)
  if not path.is_dir():
    raise ValueError(f"Model folder '{path.absolute()}' does not exist!")
  if not check_protobuf_model_files_exist(path):
    raise ValueError(
      f"Model folder '{path.absolute()}' does not contain valid protobuf model files!"
    )
  return path


def _validate_tf_file(model_path: Any) -> Path:  # noqa: ANN401
  path = Path(model_path)
  if not path.is_file():
    raise ValueError(f"Model file '{path.absolute()}' does not exist!")
  if not path.suffix == ".tflite":
    raise ValueError(
      f"Model file '{path.absolute()}' is not a valid TFLite model file!"
    )
  return path


def _validate_library(library: Any) -> LIBRARY_TYPES:  # noqa: ANN401
  if library not in VALID_LIBRARY_TYPES:
    raise ValueError(
      f"Unsupported TensorFlow library: {library}. Supported libraries are:  {', '.join(VALID_LIBRARY_TYPES)}."
    )
  if library == LIBRARY_TF:
    assert tf_installed()  # default
  elif library == LIBRARY_LITERT:
    if not litert_installed():
      raise ValueError(
        f"Parameter 'library': Library '{LIBRARY_LITERT}' is not available. Install birdnet with [litert] option."
      )
  else:
    raise AssertionError()
  return cast(LIBRARY_TYPES, library)


def _validate_kwargs(model_kwargs: dict, allowed: set[str] | None) -> dict[str, Any]:
  if allowed is None:
    not_allowed = set(model_kwargs.keys())
  else:
    not_allowed = set(model_kwargs.keys()) - allowed
  if len(not_allowed) > 0:
    raise ValueError(f"Unexpected keyword arguments: {', '.join(not_allowed)}. ")
  return model_kwargs


def load(
  model_type: str,
  version: str,
  backend: str,
  /,
  *,
  precision: str = MODEL_PRECISION_FP32,
  lang: str = MODEL_LANGUAGE_EN_US,
  **model_kwargs: object,
) -> ModelBase:
  model_type = _validate_model_type(model_type)
  backend = _validate_backend(backend)
  precision = _validate_precision(precision)
  lang = _validate_language(lang)

  if model_type == MODEL_TYPE_ACOUSTIC:
    version = _validate_acoustic_model_version(version)
    return _load_acoustic_model(
      version=version,
      backend=backend,
      precision=precision,
      lang=lang,
      **model_kwargs,
    )
  elif model_type == MODEL_TYPE_GEO:
    version = _validate_geo_model_version(version)
    return _load_geo_model(
      version=version,
      backend=backend,
      precision=precision,
      lang=lang,
      **model_kwargs,
    )
  else:
    raise AssertionError()


def _load_acoustic_model(
  version: ACOUSTIC_MODEL_VERSIONS,
  backend: MODEL_BACKENDS,
  precision: MODEL_PRECISIONS,
  lang: MODEL_LANGUAGES,
  **model_kwargs: object,
) -> AcousticModelBase:
  if version == ACOUSTIC_MODEL_VERSION_V2_4:
    return _load_acoustic_model_V2_4(
      backend=backend,
      precision=precision,
      lang=lang,
      **model_kwargs,
    )
  else:
    raise AssertionError()


def _load_geo_model(
  version: GEO_MODEL_VERSIONS,
  backend: MODEL_BACKENDS,
  precision: MODEL_PRECISIONS,
  lang: MODEL_LANGUAGES,
  **model_kwargs: object,
) -> GeoModelBase:
  if version == GEO_MODEL_VERSION_V2_4:
    if precision != MODEL_PRECISION_FP32:
      raise ValueError(
        f"Unsupported model precision for geo model: {precision}. Currently supported precision is: {MODEL_PRECISION_FP32}."
      )
    return _load_geo_model_V2_4(backend, lang, **model_kwargs)
  else:
    raise AssertionError()


def _load_acoustic_model_V2_4(
  backend: MODEL_BACKENDS,
  precision: MODEL_PRECISIONS,
  lang: MODEL_LANGUAGES,
  **model_kwargs: object,
) -> AcousticModelBaseV2_4:
  if backend == MODEL_BACKEND_TF:
    model_kwargs = _validate_kwargs(model_kwargs, {"library"})
    library = _validate_library(model_kwargs.get("library", LIBRARY_TF))
    return AcousticTFModelV2_4.load(lang, precision, library)
  elif backend == MODEL_BACKEND_PB:
    if precision != MODEL_PRECISION_FP32:
      raise ValueError(
        f"Unsupported model precision for acoustic pb model: {precision}. Currently supported precision is: {MODEL_PRECISION_FP32}."
      )
    model_kwargs = _validate_kwargs(model_kwargs, None)

    return AcousticPBModelV2_4.load(lang)
  else:
    raise AssertionError()


def _load_geo_model_V2_4(
  backend: MODEL_BACKENDS,
  lang: MODEL_LANGUAGES,
  **model_kwargs: object,
) -> GeoModelBase:
  if backend == MODEL_BACKEND_TF:
    model_kwargs = _validate_kwargs(model_kwargs, {"library"})
    library = _validate_library(model_kwargs.get("library", LIBRARY_TF))
    return GeoTFModelV2_4.load(lang, library)
  elif backend == MODEL_BACKEND_PB:
    model_kwargs = _validate_kwargs(model_kwargs, None)
    return GeoPBModelV2_4.load(lang)
  else:
    raise AssertionError()


def load_custom(
  model_type: str,
  version: str,
  backend: str,
  model: str | PathLike[str],
  species_list: str | PathLike[str],
  /,
  *,
  precision: str = MODEL_PRECISION_FP32,
  check_validity: bool = True,
  **model_kwargs: object,
) -> ModelBase:
  model_type = _validate_model_type(model_type)
  backend = _validate_backend(backend)
  model = _validate_path(model)
  species_list = _validate_species_list_path(species_list)
  precision = _validate_precision(precision)

  if model_type == MODEL_TYPE_ACOUSTIC:
    version = _validate_acoustic_model_version(version)
    return _load_custom_acoustic_model(
      version=version,
      backend=backend,
      precision=precision,
      model=model,
      species_list=species_list,
      check_validity=check_validity,
      **model_kwargs,
    )
  elif model_type == MODEL_TYPE_GEO:
    version = _validate_geo_model_version(version)
    return _load_custom_geo_model(
      version=version,
      backend=backend,
      model=model,
      precision=precision,
      species_list=species_list,
      check_validity=check_validity,
      **model_kwargs,
    )
  else:
    raise AssertionError()


def _load_custom_acoustic_model(
  version: ACOUSTIC_MODEL_VERSIONS,
  backend: MODEL_BACKENDS,
  precision: MODEL_PRECISIONS,
  model: Path,
  species_list: Path,
  check_validity: bool,
  **model_kwargs: object,
) -> AcousticModelBase:
  if version == ACOUSTIC_MODEL_VERSION_V2_4:
    return _load_custom_acoustic_model_V2_4(
      backend=backend,
      precision=precision,
      species_list=species_list,
      model=model,
      check_validity=check_validity,
      **model_kwargs,
    )
  else:
    raise AssertionError()


def _load_custom_geo_model(
  version: GEO_MODEL_VERSIONS,
  backend: MODEL_BACKENDS,
  model: Path,
  precision: MODEL_PRECISIONS,
  species_list: Path,
  check_validity: bool,
  **model_kwargs: object,
) -> GeoModelBase:
  if version == GEO_MODEL_VERSION_V2_4:
    if precision != MODEL_PRECISION_FP32:
      raise ValueError(
        f"Unsupported model precision for geo model: {precision}. Currently supported precision is: {MODEL_PRECISION_FP32}."
      )
    return _load_custom_geo_model_V2_4(
      backend, model, species_list, check_validity, **model_kwargs
    )
  else:
    raise AssertionError()


def _load_custom_acoustic_model_V2_4(
  backend: MODEL_BACKENDS,
  precision: MODEL_PRECISIONS,
  model: Path,
  species_list: Path,
  check_validity: bool,
  **model_kwargs: object,
) -> AcousticModelBaseV2_4:
  if backend == MODEL_BACKEND_TF:
    model = _validate_tf_file(model)
    model_kwargs = _validate_kwargs(model_kwargs, {"library"})
    library = _validate_library(model_kwargs.get("library", LIBRARY_TF))

    return AcousticTFModelV2_4.load_custom(
      model, species_list, precision, check_validity, library
    )
  elif backend == MODEL_BACKEND_PB:
    if precision != MODEL_PRECISION_FP32:
      raise ValueError(
        f"Unsupported model precision for acoustic pb model: {precision}. Currently supported precision is: {MODEL_PRECISION_FP32}."
      )
    model = _validate_pb_model_folder(model)
    model_kwargs = _validate_kwargs(model_kwargs, None)
    return AcousticPBModelV2_4.load_custom(model, species_list, check_validity)
  else:
    raise AssertionError()


def _load_custom_geo_model_V2_4(
  backend: MODEL_BACKENDS,
  model: Path,
  species_list: Path,
  check_validity: bool,
  **model_kwargs: object,
) -> GeoModelBase:
  if backend == MODEL_BACKEND_TF:
    model = _validate_tf_file(model)
    model_kwargs = _validate_kwargs(model_kwargs, {"library"})
    library = _validate_library(model_kwargs.get("library", LIBRARY_TF))
    return GeoTFModelV2_4.load_custom(model, species_list, check_validity, library)
  elif backend == MODEL_BACKEND_PB:
    model = _validate_pb_model_folder(model)
    model_kwargs = _validate_kwargs(model_kwargs, None)
    return GeoPBModelV2_4.load_custom(model, species_list, check_validity)
  else:
    raise AssertionError()
