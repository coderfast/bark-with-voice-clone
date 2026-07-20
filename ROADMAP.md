# ROADMAP.md - Improvement Tasks

## Overview

This document outlines the tasks to improve the bark-with-voice-clone codebase, organized by priority and category. Based on a thorough code review of all files (excluding `app_clone_voice/`).

---

## Priority 1: Critical Bugs & Compatibility ✅ DONE

### 1.1 Python Version Compatibility Fix ✅
- **File:** `hubert/customtokenizer.py:153`
- **Issue:** `load_model: str | None = None` uses Python 3.10+ syntax, but `pyproject.toml` requires `>=3.8`
- **Fix:** Changed to `Optional[str]` from `typing` module

### 1.2 Broken LoRA eval/train Mode ✅
- **File:** `utils/lora.py:43-49`
- **Issue:** `eval()` and `train()` overrides don't call `super().eval()`/`super().train()`, breaking PyTorch's module mode propagation
- **Fix:** Added `super().eval()` and `super().train()` calls

### 1.3 Global Logging Suppression ✅
- **File:** `hubert/pre_kmeans_hubert.py:23`
- **Issue:** `logging.root.setLevel(logging.ERROR)` suppresses ALL logging in the entire process
- **Fix:** Changed to module-specific logger: `logging.getLogger(__name__).setLevel(logging.ERROR)`

### 1.4 Hardcoded CUDA Device ✅
- **File:** `hubert/customtokenizer.py:82,158,161,183`
- **Issue:** Hardcoded `'cuda'` crashes on CPU-only machines
- **Fix:** Added device auto-detection with `torch.device('cuda' if torch.cuda.is_available() else 'cpu')`

### 1.5 Bare except Clauses ✅
- **File:** `bark/generation.py:425,601,762`
- **Issue:** Bare `except:` swallows all exceptions including `KeyboardInterrupt`, `SystemExit`
- **Fix:** Changed to `except KeyError:` (these handle backward-compatible key names)

### 1.6 Package Installation Missing Packages ✅
- **File:** `pyproject.toml`
- **Issue:** `hubert/` and `utils/` packages not listed in `[tool.setuptools] packages`
- **Fix:** Changed to `packages = ["bark", "hubert", "utils"]`

### 1.7 License Configuration Mismatch ✅
- **File:** `pyproject.toml:14-15`
- **Issue:** Comment says "Apache 2.0" but actual LICENSE.md is MIT; `license = {file = "LICENSE"}` points to non-existent file
- **Fix:** Changed to `license = {file = "LICENSE.md"}` and updated comment to "MIT"

---

## Priority 2: Missing Dependencies ✅ DONE

### 2.1 Core Dependencies ✅
- **File:** `pyproject.toml`
- **Missing from core deps:**
  - `huggingface-hub` (used in `bark/generation.py`)
  - `torchaudio` (used in notebooks and training)
  - `fairseq` (used in `hubert/pre_kmeans_hubert.py` and `rvc_infer.py`)

### 2.2 Training Dependencies ✅
- **File:** `pyproject.toml`
- **Missing from optional deps:**
  - `accelerate` (used in training notebooks)
  - `diffusers` (used for LR schedulers)
  - `wandb` (optional logging)
  - `bitsandbytes` (optional quantization)

---

## Priority 3: Code Quality - Bark Core ✅ DONE

### 3.1 Extract Duplicated Sampling Logic ✅
- **File:** `bark/generation.py`
- **Issue:** Top-p/top-k sampling code duplicated 3 times
- **Fix:** Extracted to `_apply_top_k_top_p(logits, top_k, top_p)` helper function

### 3.2 Extract Duplicated Model Loading Pattern ✅
- **File:** `bark/generation.py`
- **Issue:** "Load model if not exist" pattern duplicated 4 times
- **Fix:** Extracted to `_ensure_model_loaded(model_type)` helper

### 3.3 Extract Duplicated MPS Workaround ✅
- **File:** `bark/generation.py`
- **Issue:** "multinomial bugged on mps" workaround duplicated 3 times
- **Fix:** Extracted to `_safe_multinomial(probs, num_samples)` helper

### 3.4 Fix lm_heads Key Fixup ✅
- **File:** `bark/generation.py`
- **Issue:** 7 manually repeated `if` statements for state dict key fixup
- **Fix:** Replaced with loop: `for i in range(7): ...`

### 3.5 Fix API Design Issues ✅
- **File:** `bark/api.py`
- **Issues:**
  - `save_as_prompt` uses `assert` for validation (stripped with `-O`)
  - `generate_audio` returns inconsistent types (tuple vs ndarray)
  - `temp=0.5` hardcoded for fine generation
- **Fix:**
  - Replaced `assert` with proper `ValueError`/`TypeError` raises
  - Added docstrings documenting return types
  - Added `fine_temp` parameter to `semantic_to_waveform` and `generate_audio`

### 3.6 Add Type Hints to Generation Functions ✅
- **File:** `bark/generation.py`
- **Issue:** None of the 20+ functions have type hints
- **Fix:** Added type hints to all public functions and helper functions

### 3.7 Fix Global State Management ✅
- **File:** `bark/generation.py`
- **Issue:** Module-level `global` declaration is redundant
- **Fix:** Removed redundant `global` keyword, added type annotations to dicts

### 3.8 Fix Environment Variable String-vs-Bool ✅
- **File:** `bark/generation.py`
- **Issue:** `os.environ.get` returns strings, but used as booleans
- **Fix:** Added `_str_to_bool()` helper function for proper conversion

### 3.9 Remove Unused Constant ✅
- **File:** `bark/generation.py`
- **Issue:** `CONTEXT_WINDOW_SIZE = 1024` defined but never used
- **Fix:** Removed unused constant

### 3.10 Fix print vs logger Inconsistency ✅
- **File:** `bark/generation.py`
- **Issue:** Uses `print()` instead of `logger.warning()` for extra keys
- **Fix:** Changed to `logger.warning(f"extra keys found: {extra_keys}")`

---

## Priority 4: Code Quality - Hubert & Utils ✅ DONE

### 4.1 Fix Hubert Manager Relative Paths ✅
- **File:** `hubert/hubert_manager.py`
- **Issue:** Uses relative path which depends on CWD
- **Fix:** Changed to path relative to module file using `_MODULE_DIR`

### 4.2 Add Download Verification ✅
- **File:** `hubert/hubert_manager.py`
- **Issue:** Downloads files with no integrity verification
- **Fix:** Added SHA256 hash verification with `_compute_sha256()` and `_verify_download()` helpers

### 4.3 Remove Dead Code in pre_kmeans_hubert ✅
- **File:** `hubert/pre_kmeans_hubert.py`
- **Issue:** Unused `default()` function, commented-out kmeans code, unnecessary numpy roundtrip
- **Fix:** Removed dead code, simplified tensor operations (removed numpy roundtrip)

### 4.4 Fix Device Handling in pre_kmeans_hubert ✅
- **File:** `hubert/pre_kmeans_hubert.py`
- **Issue:** Double device placement (once on empty module, then on loaded model)
- **Fix:** Removed first `self.to(device)` call, moved device placement after model loading

### 4.5 Fix bitsandbytes Duplicate Imports ✅
- **File:** `utils/bitsandbytes.py`
- **Issue:** `copy`/`deepcopy` imported twice; `torch` imported twice
- **Fix:** Removed duplicate `copy` import

### 4.6 Remove bitsandbytes Copy-Paste Artifacts ✅
- **File:** `utils/bitsandbytes.py`
- **Issue:** Shebang line and Apache header appear in middle of file
- **Fix:** Removed the misplaced header block (lines 291-306)

### 4.7 Fix bitsandbytes Docstring ✅
- **File:** `utils/bitsandbytes.py`
- **Issue:** `to_json_file` docstring mentions non-existent `use_diff` parameter
- **Fix:** Updated docstring to match actual signature

### 4.8 Fix LoRA Weight Storage ✅
- **File:** `utils/lora.py`
- **Issue:** `self.weight = weight` stored as attribute, not `nn.Parameter` (won't move with `model.to()`)
- **Fix:** Changed to `self.register_buffer('weight', weight)` so it moves with the model

---

## Priority 5: Code Quality - RVC & Notebooks ✅ DONE

### 5.1 Clean Up rvc_infer.py ✅
- **File:** `rvc_infer.py`
- **Issues:**
  - Duplicate imports (lines 1, 6)
  - Duplicate `now_dir`/`sys.path.append` (lines 2-3, 110-112)
  - Unused `pdb` import (line 1)
  - Extensive global mutable state
  - Chinese comments without English equivalents
- **Fix:** Removed duplicates, added English comments, documented global state requirements, added type hints

### 5.2 Fix .gitignore ✅
- **File:** `.gitignore`
- **Missing entries:**
  - `__hugginface_downloads/` (note: typo in directory name)
  - `.ipynb_checkpoints/`
  - `*.egg-info/`
  - `build/`
  - `dist/`
  - `.env`
  - `venv/`, `.venv/`
  - `.mypy_cache/`
  - `.pytest_cache/`
- **Overly specific entries to generalize:**
  - `joe_biden_state_of_union/` → `datasets/*/`
  - `devin-youtube/` (removed)

### 5.3 Extract Shared Notebook Utilities ✅
- **File:** `utils/training.py` (new)
- **Issue:** ~400-500 lines of code duplicated across each pair of notebooks
- **Functions extracted:**
  - `_clear_cuda_cache()`, `_md5()`, `_download()`
  - `_tokenize()`, `_detokenize()`, `_normalize_whitespace()`
  - `REMOTE_MODEL_PATHS` dict, `load_filepaths_and_text()`
  - `_load_model()`, `_flatten_codebooks()`, `_get_duration()`
  - `TtsDataset` class, `TtsCollater` class

### 5.4 Extract Shared Generation Utilities ✅
- **File:** `utils/generation.py` (new)
- **Issue:** `generate_with_settings()` duplicated 3 times, `split_and_recombine_text()` duplicated in 2 notebooks
- **Functions extracted:**
  - `split_and_recombine_text()`
  - `generate_with_settings()`
  - `play_audio()`, `save_audio()`

### 5.5 Fix train_fine.ipynb Tracker Name ✅
- **File:** `train_fine.ipynb`
- **Issue:** `accelerator.init_trackers("bark_coarse", config={})` should be `"bark_fine"`
- **Fix:** Changed to `"bark_fine"`

### 5.6 Remove Unused Imports in Training Notebooks ✅
- **Files:** `train_coarse.ipynb`, `train_fine.ipynb`
- **Issue:** Import `BertTokenizer` but never use it (only used in `train_semantic.ipynb`)
- **Fix:** Removed unused BertTokenizer imports

### 5.7 Remove Commented-Out Quantization Code ✅
- **Files:** All training notebooks
- **Issue:** ~30 lines of commented-out quantization code in each notebook
- **Fix:** Removed commented-out code blocks, kept only active quantization_config definition

---

## Priority 6: Documentation & Polish ✅ DONE

### 6.1 Add Docstrings to Public API Functions ✅
- **Files:** `bark/api.py`, `bark/generation.py`
- **Issue:** Most functions lack docstrings or have minimal documentation
- **Fix:** Added comprehensive docstrings to key functions: `_download()`, `InferenceContext`, `_clear_cuda_cache()`, `clean_models()`, `_load_model()`, `_load_codec_model()`, `load_model()`, `load_codec_model()`, `preload_models()`

### 6.2 Document Magic Numbers ✅
- **File:** `bark/generation.py`
- **Issue:** Hardcoded values like 256, 768, 512, 1024 without explanation
- **Fix:** Added comments explaining all magic numbers in constants section:
  - `SEMANTIC_RATE_HZ = 49.9  # Semantic token rate in Hz (one token per ~20ms)`
  - `SEMANTIC_VOCAB_SIZE = 10_000  # Number of semantic tokens`
  - `CODEBOOK_SIZE = 1024  # Size of each EnCodec codebook (10 bits per codebook entry)`
  - `N_COARSE_CODEBOOKS = 2  # Number of codebooks used in coarse generation`
  - `N_FINE_CODEBOOKS = 8  # Total number of codebooks in EnCodec`
  - `COARSE_RATE_HZ = 75  # Coarse token rate in Hz`
  - `SAMPLE_RATE = 24_000  # Output audio sample rate in Hz`

### 6.3 Remove Commented-Out Code ✅
- **Files:** `bark/generation.py`, `bark/model.py`
- **Issues:**
  - `bark/generation.py:271-276` (checksum validation) - Removed
  - `bark/model.py:43` (print statement) - Removed
- **Fix:** Removed all commented-out code blocks

### 6.4 Fix Incomplete Documentation ✅
- **File:** `hubert/customtokenizer.py`
- **Issue:** `get_token` docstring is truncated: "Used to get the token for the first"
- **Fix:** Completed docstring with full description of purpose, args, and return value

### 6.5 Add Error Messages to Assertions ✅
- **File:** `bark/generation.py`
- **Issue:** Bare `assert` statements without error messages
- **Fix:** Added descriptive error messages to 10 key assertions:
  - `assert isinstance(text, str), f"text must be a string, got {type(text)}"`
  - `assert len(text.strip()) > 0, "text must not be empty or contain only whitespace"`
  - `assert x.shape[1] == 256 + 256 + 1, f"Input shape mismatch..."`
  - `assert all(0 <= out) and all(out < SEMANTIC_VOCAB_SIZE), "Generated tokens out of valid range"`
  - `assert len(arr.shape) == 2, f"Expected 2D array, got {len(arr.shape)}D"`
  - `assert 60 <= max_coarse_history <= 630, f"max_coarse_history must be between 60 and 630..."`
  - `assert max_coarse_history + sliding_window_len <= 1024 - 256, "max_coarse_history + sliding_window_len exceeds limit"`
  - `assert n_steps > 0 and n_steps % N_COARSE_CODEBOOKS == 0, f"n_steps must be positive..."`
  - `assert len(gen_coarse_arr) == n_steps, f"Generated length mismatch..."`
  - `assert gen_fine_arr.shape[-1] == x_coarse_gen.shape[-1], "Output length must match input length"`

---

## Implementation Order

1. **Phase 1 - Critical Fixes** (Priority 1): Fix compatibility bugs, broken LoRA, logging suppression
2. **Phase 2 - Dependencies** (Priority 2): Update pyproject.toml with missing packages
3. **Phase 3 - Core Refactor** (Priority 3): Extract duplicated code, fix API issues
4. **Phase 4 - Utils Cleanup** (Priority 4): Fix hubert/utils issues
5. **Phase 5 - Notebook Cleanup** (Priority 5): Extract shared utilities, fix notebooks
6. **Phase 6 - Documentation** (Priority 6): Add docstrings, clean up comments

---

## Verification

After each phase:
1. Run `python -c "from bark import generate_audio, preload_models"` to verify imports work
2. Run `python -c "from hubert.customtokenizer import CustomTokenizer"` to verify hubert imports
3. Run `python -c "from utils.lora import convert_linear_layer_to_lora"` to verify utils imports
4. Check that notebooks can be opened without syntax errors
5. Verify `pip install .` installs all packages correctly
