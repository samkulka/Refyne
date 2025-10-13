import csv
import random
from datetime import datetime, timedelta

# Generate realistic customer data
first_names = ["Sarah", "Michael", "Jennifer", "David", "Jessica", "James", "Emily", "Robert", "Lisa", "William",
               "Ashley", "Christopher", "Amanda", "Daniel", "Stephanie", "Matthew", "Michelle", "Joshua", "Nicole", "Andrew"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
cities = ["Austin, TX", "Denver, CO", "Seattle, WA", "Portland, OR", "Nashville, TN", "Charlotte, NC", "Phoenix, AZ",
          "San Diego, CA", "Boston, MA", "Atlanta, GA", "Miami, FL", "Chicago, IL", "New York, NY", "Los Angeles, CA"]
companies = ["Tech Corp", "Data Systems Inc", "Cloud Solutions", "AI Innovations", "Web Services LLC", "Digital Media Co",
             "Software Partners", "Analytics Group", "Platform Inc", "Network Solutions"]
emails_providers = ["gmail.com", "yahoo.com", "outlook.com", "company.com", "business.net"]

def generate_email(first, last, provider):
    return f"{first.lower()}.{last.lower()}@{provider}"

def generate_phone():
    return f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

def generate_date(days_back=365):
    date = datetime.now() - timedelta(days=random.randint(0, days_back))
    return date.strftime("%Y-%m-%d")

# Generate 1000 customer records
num_records = 1000
output_file = "customer_data_1000.csv"

print(f"Generating {num_records} customer records...")

with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'company',
                  'city', 'account_value', 'last_active', 'num_accounts', 'growth_rate', 'status']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for i in range(1, num_records + 1):
        first = random.choice(first_names)
        last = random.choice(last_names)

        # Introduce some data quality issues
        email = generate_email(first, last, random.choice(emails_providers))
        if random.random() < 0.05:  # 5% missing emails
            email = ""

        phone = generate_phone()
        if random.random() < 0.08:  # 8% missing phones
            phone = ""

        company = random.choice(companies)
        if random.random() < 0.03:  # 3% missing companies
            company = ""

        city = random.choice(cities)
        account_value = round(random.uniform(1000, 100000), 2)
        last_active = generate_date(180)
        num_accounts = random.randint(1, 5)
        growth_rate = round(random.uniform(-10, 25), 1)
        status = random.choice(["active", "inactive", "pending", "churned"])

        writer.writerow({
            'customer_id': f"CUST-{i:05d}",
            'first_name': first,
            'last_name': last,
            'email': email,
            'phone': phone,
            'company': company,
            'city': city,
            'account_value': account_value,
            'last_active': last_active,
            'num_accounts': num_accounts,
            'growth_rate': growth_rate,
            'status': status
        })

print(f"✅ Generated {num_records} records in {output_file}")
print(f"\nData quality issues included:")
print(f"  - ~5% missing emails")
print(f"  - ~8% missing phone numbers")
print(f"  - ~3% missing companies")
print(f"\nYou can now upload this file to test your Refyne app!")
