import random

from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import sessionmaker

from hybridrag.ingest.db import Base, get_engine
from hybridrag.models import Chunk


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    department = Column(String(100))
    title = Column(String(100))
    email = Column(String(100))
    manager = Column(String(100))
    hire_date = Column(String(20))
    salary = Column(Float)
    location = Column(String(100))

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(String(50), unique=True, index=True)
    vendor_name = Column(String(100))
    category = Column(String(100))
    risk_score = Column(String(20))
    contract_owner = Column(String(100))
    annual_spend = Column(Float)
    status = Column(String(50))
    renewal_date = Column(String(20))

class ExpensePolicyTable(Base):
    __tablename__ = "expense_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_code = Column(String(50), unique=True, index=True)
    expense_category = Column(String(100))
    limit_amount = Column(Float)
    requires_receipt = Column(String(10))
    requires_manager_approval = Column(String(10))
    notes = Column(Text)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def seed_structured_data():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(Employee).count() > 0:
        print("Structured tables already seeded.")
        session.close()
        return

    departments = ["HR", "Security", "Finance", "Engineering", "Product", "Legal"]
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George", "Hannah", "Ian", "Julia"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]

    for i in range(1, 151):
        emp_id = f"EMP-{i:03d}"
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        dept = random.choice(departments)
        emp = Employee(
            employee_id=emp_id,
            full_name=f"{fname} {lname}",
            department=dept,
            title=f"Senior {dept} Specialist",
            email=f"{fname.lower()}.{lname.lower()}@enterprise.internal",
            manager=f"Manager {dept}",
            hire_date="2022-03-15",
            salary=85000.0 + (i * 250.0),
            location="San Francisco, CA"
        )
        session.add(emp)

    vendor_cats = ["Cloud Infrastructure", "SaaS", "Security", "Legal", "Facilities", "Travel"]
    for i in range(1, 151):
        v_id = f"VEND-{i:03d}"
        v = Vendor(
            vendor_id=v_id,
            vendor_name=f"Vendor Corp Alpha {i}",
            category=random.choice(vendor_cats),
            risk_score=random.choice(["Low", "Medium", "High"]),
            contract_owner=random.choice(["Alice Smith", "Bob Ross", "Jane Doe", "Frank Castle"]),
            annual_spend=10000.0 * i,
            status="Active",
            renewal_date="2025-12-31"
        )
        session.add(v)

    exp_cats = ["Client Travel", "Team Dinner", "Software Subscriptions", "Office Supplies", "Conference Registration", "Client Entertainment"]
    for i in range(1, 101):
        code = f"EXP-{i:03d}"
        ep = ExpensePolicyTable(
            policy_code=code,
            expense_category=random.choice(exp_cats),
            limit_amount=50.0 * i,
            requires_receipt="Yes" if i > 10 else "No",
            requires_manager_approval="Yes" if i > 20 else "No",
            notes=f"Standard reimbursement limit for category tier {i}. Requires itemized receipt and manager sign-off if exceeding threshold."
        )
        session.add(ep)

    session.commit()
    print(f"Seeded structured tables: {session.query(Employee).count()} employees, {session.query(Vendor).count()} vendors, {session.query(ExpensePolicyTable).count()} expense policies.")
    session.close()

def load_structured_chunks() -> list[Chunk]:
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    chunks = []

    employees = session.query(Employee).all()
    for emp in employees:
        content = f"Record Card: Employee\nID: {emp.employee_id}\nName: {emp.full_name}\nDepartment: {emp.department}\nTitle: {emp.title}\nEmail: {emp.email}\nManager: {emp.manager}\nHire Date: {emp.hire_date}\nSalary: ${emp.salary:,.2f}\nLocation: {emp.location}"
        chunks.append(Chunk(
            chunk_id=f"STR-EMP-{emp.employee_id}",
            doc_id=emp.employee_id,
            title=f"Employee Record: {emp.full_name}",
            category="hr_policy",
            department=emp.department,
            effective_date=emp.hire_date,
            owner=emp.manager,
            sensitivity="confidential",
            heading_path=["Structured Records", "Employees", emp.department],
            content=content,
            source_type="structured"
        ))

    vendors = session.query(Vendor).all()
    for v in vendors:
        content = f"Record Card: Vendor\nID: {v.vendor_id}\nName: {v.vendor_name}\nCategory: {v.category}\nRisk Score: {v.risk_score}\nContract Owner: {v.contract_owner}\nAnnual Spend: ${v.annual_spend:,.2f}\nStatus: {v.status}\nRenewal Date: {v.renewal_date}"
        chunks.append(Chunk(
            chunk_id=f"STR-VEND-{v.vendor_id}",
            doc_id=v.vendor_id,
            title=f"Vendor Record: {v.vendor_name}",
            category="vendor_contract",
            department="Procurement",
            effective_date=v.renewal_date,
            owner=v.contract_owner,
            sensitivity="internal",
            heading_path=["Structured Records", "Vendors", v.category],
            content=content,
            source_type="structured"
        ))

    exp_policies = session.query(ExpensePolicyTable).all()
    for ep in exp_policies:
        content = f"Record Card: Expense Policy\nCode: {ep.policy_code}\nCategory: {ep.expense_category}\nLimit Amount: ${ep.limit_amount:,.2f}\nRequires Receipt: {ep.requires_receipt}\nRequires Manager Approval: {ep.requires_manager_approval}\nNotes: {ep.notes}"
        chunks.append(Chunk(
            chunk_id=f"STR-EXP-{ep.policy_code}",
            doc_id=ep.policy_code,
            title=f"Expense Policy Record: {ep.expense_category} ({ep.policy_code})",
            category="finance_sop",
            department="Finance",
            effective_date="2025-01-01",
            owner="Penny Cents",
            sensitivity="internal",
            heading_path=["Structured Records", "Expense Policies", ep.expense_category],
            content=content,
            source_type="structured"
        ))

    session.close()
    return chunks

if __name__ == "__main__":
    seed_structured_data()
