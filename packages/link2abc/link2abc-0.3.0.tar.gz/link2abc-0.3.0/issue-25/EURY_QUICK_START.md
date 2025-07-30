# EURY QUICK START - Ubuntu Testing Protocol
# ♠️🌿🎸🤖🧵 G.MUSIC ASSEMBLY MODE

## 🚀 IMMEDIATE ACTIONS FOR EURY

**Time Estimate**: 60-90 minutes total testing
**Ubuntu Requirements**: Python 3.8+, pip, git

### STEP 1: Setup (5 minutes)
```bash
git clone https://github.com/jgwill/EchoThreads.git
cd EchoThreads/music/linktune/issue-25
git checkout 25-link2abc-hf-chatmusician-integration
```

### STEP 2: Install Dependencies (10 minutes)
```bash
pip install orpheuspypractice jgcmlib jghfmanager
which ohfi  # Should find the command
```

### STEP 3: Quick API Test (5 minutes)
```bash
python simple_hf_test.py
# Input your HuggingFace API key when prompted
# Get key from: https://huggingface.co/settings/tokens
```

### STEP 4: Core Integration Test (15 minutes)
```bash
# Create test file
cat > test.abc << 'EOF'
X:1
T:Test
M:4/4
L:1/8
K:G
|: G2 A2 B2 c2 :|
EOF

# Test integration
python integration_cli_demo.py test.abc --enhance-hf --hf-budget 0.25
```

### STEP 5: Validate Results (10 minutes)
```bash
# Check output structure
tree output/ || find output/ -type f
# Should show original/ and enhanced/ directories
```

## 🎯 SUCCESS CRITERIA
- [ ] ohfi command available
- [ ] HuggingFace API connects successfully  
- [ ] Dual outputs created (original + enhanced)
- [ ] No API keys stored in files
- [ ] Budget controls work

## 📋 REPORT BACK TO JERRY
Create file: `ledger/eury_test_results_YYYYMMDD.md` with:
- ✅/❌ for each test phase
- Error messages if any
- Performance observations
- PyPI readiness assessment

**Full details in**: `HANDOFF_TO_EURY.md`