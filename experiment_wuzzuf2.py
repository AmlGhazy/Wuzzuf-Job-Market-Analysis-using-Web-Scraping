from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

def setup_driver():
    options=Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

def search_jobs():
    driver=setup_driver()
    wait = WebDriverWait(driver, 10)
    data=[]
    website=f"https://wuzzuf.net/jobs/egypt/"
    driver.get(website)
    # Search for analyst jobs
    search_box = wait.until(
    EC.presence_of_element_located((By.NAME, "q"))
    )
    search_box.send_keys("analyst" + Keys.ENTER)
    
    # Open Country Filter
    country = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//h3//span[text()='Country']/../i")
        )
    )
    country.click()

    # Select Egypt
    egypt_checkbox = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//label[.//span[text()='Egypt']]")
        )
    )
    egypt_checkbox.click()
    
    # Open City Filter
    city = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//h3//span[text()='City']/../i")
        )
    )
    city.click()

    # Select Cairo
    cairo_checkbox = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//label[.//span[text()='Cairo']]")
        )
    )
    cairo_checkbox.click()

    while True:
        Jobs=driver.find_elements(By.CLASS_NAME,"css-ghe2tq")
        if not Jobs:
            break 
        for job in Jobs:
            try:
                job_name=job.find_element(By.XPATH,".//h2//a").text.strip()
                location=job.find_element(By.XPATH,".//div//span").text.strip()  
                company_name=job.find_element(By.XPATH,".//a[contains(@class,'css-ipsyv7')]").text.strip()
                #clean company_name
                company_name = company_name.replace(" -", "").strip()
                job_detailed=job.find_element(By.CLASS_NAME,"css-1rhj4yg").text.strip()
                #clean Job_Detailed
                job_detailed = job_detailed.replace("\n", " ")
                job_detailed = job_detailed.replace(job_name, "")
                job_detailed = re.sub(r"\s+", " ", job_detailed)
                parts=[x.strip() for x in job_detailed.split("·")]
                employment_type=parts[0].replace("Experienced","")
                # split Employment Type Column
                Employment_Type=""
                work_mode=""
                level=""
                for item in employment_type.split("."):
                    item=item.strip()
                    #Employment_Type
                    if "Full Time" in item:
                        Employment_Type="Full Time"
                    elif "Part Time" in item:
                        Employment_Type="Part Time"

                    #work_mode
                    if "On-site" in item:
                        work_mode="On-site"
                    elif "Remote" in item:
                        work_mode = "Remote"
                    elif "Hybrid" in item:
                        work_mode = "Hybrid"

                    # Level 
                    if "Entry Level" in item:
                        level = "Entry Level"
                    elif "Freelance" in item or "Project" in item:
                        level = "Freelance / Project"    
                Experience = re.search(r"(\d+\s*-\s*\d+|\d+\+?)\s*Yrs of Exp", job_detailed)
                Experience = Experience.group(1) if Experience else "Not Specified"
                job_skills=" | ".join(parts[2:])
                if "analyst" in job_name.lower():
                    data.append({"Job Name":job_name,"Location":location,
                                "Company_Name":company_name,
                                "Employment Type":Employment_Type,
                                "work_mode":work_mode,
                                "Level":level,
                                "Experience":Experience,
                                "Skills":job_skills
                            })   
            except Exception as error:
                print(f"Error processing job: {error}")        
        #Next Page          
        try:
            old_url = driver.current_url
            next_button = wait.until(
               EC.element_to_be_clickable(
                  (By.XPATH, "(//ul//li//a)[last()]")
                )
            )
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            new_url = driver.current_url
            if old_url==new_url:
                break
        except:
            break    
    print("Scrapping Finished Successfully.")
    driver.quit()
    df=pd.DataFrame(data)
    df.to_csv('Jobs.csv',index=False,encoding="utf-8-sig")
    return df
final_data=search_jobs()    
print(final_data.head())