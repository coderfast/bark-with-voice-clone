# ROADMAP.md - Improvement Tasks

## Overview

This document outlines the tasks to improve the bark-with-voice-clone codebase, organized by priority and category.

---

## Priority 1: Critical Bugs & Compatibility ✅ DONE

### 1.1 Python Version Compatibility Fix ✅
- **File:** `hubert/customtokenizer.py`
- **Issue:** `str | None` uses Python 3.10+ syntax
- **Fix:** Changed to `Optional[str]`

### 1.2 Broken LoRA eval/train Mode ✅
- **File:** `utils/lora.py`
- **Issue:** `eval()` and `train()` don't call `super()`
- **Fix:** Added `super().eval()` and `super().train()` calls

### 1.3 Global Logging Suppression ✅
- **File:** `hubert/pre_kmeans_hubert.py`
- **Issue:** `logging.root.setLevel(logging.ERROR)` suppresses all logging
- **Fix:** Changed to module-specific logger

### 1.4 Hardcoded CUDA Device ✅
- **File:** `hubert/customtokenizer.py`
- **Issue:** Hardcoded `'cuda'` crashes on CPU-only machines
- **Fix:** Added device auto-detection

### 1.5 Bare except Clauses ✅
- **File:** `bark/generation.py`
- **Issue:** Bare `except:` swallows all exceptions
- **Fix:** Changed to `except KeyError:`

### 1.6 Package Installation Missing Packages ✅
- **File:** `pyproject.toml`
- **Issue:** `hubert/` and `utils/` not listed
- **Fix:** Added to packages list

### 1.7 License Configuration Mismatch ✅
- **File:** `pyproject.toml`
- **Issue:** Wrong license file reference
- **Fix:** Changed to `LICENSE.md` with MIT comment

---

## Priority 2: Missing Dependencies ✅ DONE

### 2.1 Core Dependencies ✅
- **Added:** `huggingface-hub`, `torchaudio`, `fairseq`

### 2.2 Training Dependencies ✅
- **Added:** `accelerate`, `diffusers`, `wandb`, `bitsandbytes`

---

## Priority 3: Code Quality - Bark Core ✅ DONE

### 3.1 Extract Duplicated Sampling Logic ✅
- **Helper:** `_apply_top_k_top_p(logits, top_k, top_p)`

### 3.2 Extract Duplicated Model Loading Pattern ✅
- **Helper:** `_ensure_model_loaded(model_type)`

### 3.3 Extract Duplicated MPS Workaround ✅
- **Helper:** `_safe_multinomial(probs, num_samples)`

### 3.4 Fix lm_heads Key Fixup ✅
- **Fix:** Replaced 7 if statements with loop

### 3.5 Fix API Design Issues ✅
- **Fix:** Added proper validation, `fine_temp` parameter

### 3.6 Add Type Hints to Generation Functions ✅
- **Fix:** Added comprehensive docstrings with Args/Returns

### 3.7 Fix Global State Management ✅
- **Fix:** Removed redundant `global` keyword

### 3.8 Fix Environment Variable String-vs-Bool ✅
- **Helper:** `_str_to_bool(value)`

### 3.9 Remove Unused Constant ✅
- **Fix:** Removed `CONTEXT_WINDOW_SIZE`

### 3.10 Fix print vs logger Inconsistency ✅
- **Fix:** Changed to `logger.warning()`

---

## Priority 4: Code Quality - Hubert & Utils ✅ DONE

### 4.1 Fix Hubert Manager Relative Paths ✅
- **Fix:** Used `_MODULE_DIR` for paths

### 4.2 Add Download Verification ✅
- **Helpers:** `_compute_sha256()`, `_verify_download()`

### 4.3 Remove Dead Code in pre_kmeans_hubert ✅
- **Fix:** Removed unused functions and comments

### 4.4 Fix Device Handling in pre_kmeans_hubert ✅
- **Fix:** Removed double device placement

### 4.5 Fix bitsandbytes Duplicate Imports ✅
- **Fix:** Removed duplicate `copy` import

### 4.6 Remove bitsandbytes Copy-Paste Artifacts ✅
- **Fix:** Removed misplaced header block

### 4.7 Fix bitsandbytes Docstring ✅
- **Fix:** Updated `to_json_file` docstring

### 4.8 Fix LoRA Weight Storage ✅
- **Fix:** Changed to `self.register_buffer('weight', weight)`

---

## Priority 5: Code Quality - RVC & Notebooks ✅ DONE

### 5.1 Clean Up rvc_infer.py ✅
- **Fix:** Removed duplicates, added docstrings, English comments

### 5.2 Fix .gitignore ✅
- **Fix:** Added missing entries, generalized patterns

### 5.3 Extract Shared Notebook Utilities ✅
- **New File:** `utils/training.py`

### 5.4 Extract Shared Generation Utilities ✅
- **New File:** `utils/generation.py`

### 5.5 Fix train_fine.ipynb Tracker Name ✅
- **Fix:** Changed to `"bark_fine"`

### 5.6 Remove Unused Imports in Training Notebooks ✅
- **Fix:** Removed unused `BertTokenizer` imports

### 5.7 Remove Commented-Out Quantization Code ✅
- **Fix:** Removed commented-out code blocks

---

## Priority 6: Documentation & Polish ✅ DONE

### 6.1 Add Docstrings to Public API Functions ✅
- **Fix:** Added docstrings to key functions

### 6.2 Document Magic Numbers ✅
- **Fix:** Added comments explaining constants

### 6.3 Remove Commented-Out Code ✅
- **Fix:** Removed checksum validation and print statement

### 6.4 Fix Incomplete Documentation ✅
- **Fix:** Completed `get_token` docstring

### 6.5 Add Error Messages to Assertions ✅
- **Fix:** Added descriptive error messages to 10 assertions

---

## Priority 7: New Features ✅ DONE

### 7.1 Command Line Interface ✅
- **New File:** `bark_cli.py`
- **Features:**
  - `generate` command with all audio options
  - `clone` command for voice cloning
  - `voices` command to list available voices

### 7.2 Custom Audio Format Options ✅
- **File:** `bark/api.py`
- **New Parameters:**
  - `sample_rate`: 11025, 22050, 44100 Hz
  - `bits_per_sample`: 8 or 16 bits
  - `channels`: mono or stereo

### 7.3 RVC Auto-Download ✅
- **New File:** `utils/rvc_manager.py`
- **Feature:** Automatically downloads RVC repository if not present

### 7.4 Local Model Priority ✅
- **File:** `bark/generation.py`
- **Feature:** Checks local directories before downloading

### 7.5 PyTorch 2.6+ Compatibility ✅
- **Fix:** Added `weights_only=False` to all `torch.load()` calls

---

## Implementation Order

1. **Phase 1 - Critical Fixes** (Priority 1)
2. **Phase 2 - Dependencies** (Priority 2)
3. **Phase 3 - Core Refactor** (Priority 3)
4. **Phase 4 - Utils Cleanup** (Priority 4)
5. **Phase 5 - Notebook Cleanup** (Priority 5)
6. **Phase 6 - Documentation** (Priority 6)
7. **Phase 7 - New Features** (Priority 7)

---

## Verification

After each phase:
1. Run `python -c "from bark import generate_audio, preload_models"` to verify imports
2. Run `python bark_cli.py voices` to verify CLI works
3. Run `python bark_cli.py generate "test" -o test.wav --small` to verify generation
4. Check that notebooks can be opened without syntax errors
5. Verify `pip install .` installs all packages correctly
