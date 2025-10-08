#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   Refyne API Workflow Test${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Step 1: Upload
echo -e "${YELLOW}STEP 1: Uploading file...${NC}"
UPLOAD=$(curl -s -X POST http://localhost:8000/api/v1/upload -F "file=@/tmp/test_workflow.csv")
FILE_ID=$(echo $UPLOAD | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])")
echo -e "${GREEN}✓ Uploaded! File ID: $FILE_ID${NC}"
echo ""

# Step 2: Profile
echo -e "${YELLOW}STEP 2: Profiling data quality...${NC}"
PROFILE=$(curl -s -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d "{\"file_id\": \"$FILE_ID\"}")
SCORE=$(echo $PROFILE | python3 -c "import sys, json; print(json.load(sys.stdin)['overall_quality_score'])")
ROWS=$(echo $PROFILE | python3 -c "import sys, json; print(json.load(sys.stdin)['rows'])")
COLS=$(echo $PROFILE | python3 -c "import sys, json; print(json.load(sys.stdin)['columns'])")
echo -e "${GREEN}✓ Quality Score: $SCORE/100${NC}"
echo -e "${GREEN}  Rows: $ROWS, Columns: $COLS${NC}"
echo ""

# Step 3: Clean
echo -e "${YELLOW}STEP 3: Cleaning data...${NC}"
CLEAN=$(curl -s -X POST http://localhost:8000/api/v1/clean \
  -H "Content-Type: application/json" \
  -d "{\"file_id\": \"$FILE_ID\", \"aggressive\": false}")
OUTPUT_ID=$(echo $CLEAN | python3 -c "import sys, json; print(json.load(sys.stdin)['output_file_id'])")
ROWS_BEFORE=$(echo $CLEAN | python3 -c "import sys, json; print(json.load(sys.stdin)['rows_before'])")
ROWS_AFTER=$(echo $CLEAN | python3 -c "import sys, json; print(json.load(sys.stdin)['rows_after'])")
echo -e "${GREEN}✓ Cleaned! Output ID: $OUTPUT_ID${NC}"
echo -e "${GREEN}  Rows: $ROWS_BEFORE → $ROWS_AFTER${NC}"
echo ""
echo -e "  Operations performed:"
echo $CLEAN | python3 -c "import sys, json; ops = json.load(sys.stdin)['operations_performed']; [print('    -', op) for op in ops]"
echo ""

# Step 4: Download
echo -e "${YELLOW}STEP 4: Downloading cleaned file...${NC}"
curl -s "http://localhost:8000/api/v1/download/$OUTPUT_ID?output=true" -o /tmp/cleaned_result.csv
echo -e "${GREEN}✓ Downloaded to /tmp/cleaned_result.csv${NC}"
echo ""

# Step 5: Show comparison
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   BEFORE vs AFTER${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo -e "${YELLOW}Original (first 3 rows):${NC}"
head -n 3 /tmp/test_workflow.csv
echo ""
echo -e "${YELLOW}Cleaned (first 3 rows):${NC}"
head -n 3 /tmp/cleaned_result.csv
echo ""

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}   ✓ Workflow Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
