# 🦅 Eagle-Eye 
Fetches faculty details from KIIT university website and saves to CSV

## 😃 How to use? 
1. Clone the repo
    ```bash
    git clone https://github.com/prajwal-panth/eagle-eye
    cd eagle-eye
    ```
2. Install requirements
    ```bash
    pip install -r requirements.txt
    ```
3. Run it
    ```bash
    python3 eagle-eye.py
    ```
## 😠 I need all in single copy?
```bash
git clone https://github.com/prajwal-panth/eagle-eye
cd eagle-eye
pip install -r requirements.txt
python3 eagle-eye.py
```

## 📁 Download pre-extracted CSVs:
- CSE: [cse.csv](./csv/cse.csv)
- Civil: [civil.csv](./csv/civil.csv)
- KSAS: [ksas.csv](./csv/ksas.csv)
- KSCA: [ksca.csv](./csv/ksca.csv)
- KSOH: [ksoh.csv](./csv/ksoh.csv)
- Bio-Tech: [biotech.csv](./csv/biotech.csv)
- Mechanical: [mechanical.csv](./csv/mechanical.csv)
- All Branch: [all_branch.csv](./csv/all_branch.csv)

**Note**: All branches plus un-mentioned ones are present in [all_branch.csv](./csv/all_branch.csv)

CSV is distributed as follows and in case of empty/unavailable the are left blank:<br><br>
`    NAME    |    BRANCH    |    IMAGE    |    LINKS   |    EMAIL    `<br><br>
Links are maybe multivalued attribute and are seperated by space.
