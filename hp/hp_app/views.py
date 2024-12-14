import logging
from venv import logger

from django.db import IntegrityError
from django.db.models import Max, F, Sum, Q
from django.http import JsonResponse
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from hp_app.models import Department,Jobrole,Login,Employee,Machine,Spareparts,Vendor,Stock,Item,StocktoDept,DepttoDept, Deptstock
from django.contrib import messages  # Import messages

# Create your views here.

def index(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            udata = Login.objects.get(username=username)
            if password == udata.password:  # Use hashed password checks in production
                request.session['username'] = username
                request.session['utype'] = udata.utype

                if udata.utype == 'user':
                    return redirect('index')  # Redirect to a user-specific page
                if udata.utype == 'admin':
                    return redirect('admin_dashboard')  # Adjust as necessary
                if udata.utype == 'employee':
                    return redirect('emp_dashboard')  # Adjust as necessary
            else:
                messages.error(request, 'Invalid password')
        except Login.DoesNotExist:
            messages.error(request, 'Invalid Username')

    return render(request, 'index.html')

from django.db.models import Count
from django.db.models import Sum, Count, F, Subquery, OuterRef

def admin_dashboard(request):
    # Subquery to sum the issuedqty for each sparepart from the Stock model
    stock_issued_qty = Stock.objects.filter(sparePart=OuterRef('sparepart')) \
        .values('sparePart') \
        .annotate(total_issued_qty=Sum('issuedqty')) \
        .values('total_issued_qty')[:1]  # [:1] ensures a single value per sparepart

    # Query to count spareparts and get the sum of issuedqty from the Stock table
    sparepart_counts = Spareparts.objects.values('sparepart') \
        .annotate(count=Count('sparepart')) \
        .annotate(total_issued_qty=Subquery(stock_issued_qty)) \
        .order_by('-count')

    # Pass the data to the template
    return render(request, 'admin_dashboard.html', {'sparepart_counts': sparepart_counts})

def emp_dashboard(request):
    return render(request, 'admin_dashboard.html')


def branch(request):
    if request.method == 'POST':
        branchname = request.POST.get('dept')

        Department.objects.create(department=branchname)


        return redirect('branch')  # Adjust this redirect as needed
    branches = Department.objects.all()  # Fetch all branch records from the database

    return render(request, 'branch.html', {'branches': branches})




def edit_branch(request, branch_id):
    # Get the branch object to edit
    branch = get_object_or_404(Department, id=branch_id)

    # Handle form submission
    if request.method == 'POST':
        # Manually retrieve and update the branch fields
        branch.department = request.POST.get('dept')

        branch.save()
        return redirect('branch')  # Redirect to the branch list after saving

    # Prepopulate form fields for the GET request
    return render(request, 'edit_branch.html', {'branch': branch})

def emp_list(request):
    # Fetch all employees
    employees = Employee.objects.all()

    # Pass the employees list to the template
    return render(request, 'emp_list.html', {'employees': employees})


def edit_employee(request, id):
    # Retrieve the employee object based on the provided ID
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        # Update employee fields directly from the POST data
        employee.fullname = request.POST.get('fullname')
        employee.gender = request.POST.get('gender')
        employee.email = request.POST.get('email')
        employee.city = request.POST.get('city')
        employee.state = request.POST.get('state')
        employee.taluk = request.POST.get('taluk')
        employee.district = request.POST.get('district')
        employee.pincode = request.POST.get('pincode')
        employee.contact = request.POST.get('contact')
        employee.role = request.POST.get('role')

        # Save the updated employee object
        employee.save()
        return redirect('employee_list')  # Redirect to the employee list page

    # Render the edit employee form template with the current employee data
    return render(request, 'edit_employee.html', {'employee': employee})


def generate_employee_id():
    # Fetch the last employee_id (max value) from the Employee model
    last_employee = Employee.objects.aggregate(max_id=Max('emp_id'))
    last_id = last_employee['max_id']

    # Check if we have any employees
    if last_id and last_id.startswith('MI'):
        # Extract the numeric part from the last employee ID, e.g., MI01 -> 1
        numeric_part = int(last_id[2:])  # Strip the 'MI' and convert to int
        new_numeric_part = numeric_part + 1
    else:
        new_numeric_part = 1  # Start from MI01 if no employee exists

    # Generate the new employee ID with the 'MI' prefix and leading zero padding
    new_employee_id = f'MI{new_numeric_part:02d}'  # E.g., MI01, MI02, etc.
    return new_employee_id
 # Ensure you have this utility



def employee(request):
    if request.method == 'POST':
        # Get employee details from the form
        fullname = request.POST.get('fullname')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        contact = request.POST.get('contact')
        nationality = request.POST.get('nationality')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        district = request.POST.get('district')
        Taluk = request.POST.get('Taluk')
        email = request.POST.get('email')
        adhar = request.POST.get('adhar')
        pancard = request.POST.get('pancard')

        password = request.POST.get('password')
        jobRole = request.POST.get('jobRole')
        emp_id = generate_employee_id()  # You need to implement this function

        # Get the branch selected by the user
        branch_id = request.POST.get('branchname')


        # Save Employee object
        employee = Employee.objects.create(
            fullname=fullname,
            gender=gender,
            dob=dob,
            contact=contact,
            nationality=nationality,
            city=city,
            state=state,
            pincode=pincode,
            district=district,
            Taluk=Taluk,
            email=email,
            adhar=adhar,
            pancard=pancard,
            jrole=jobRole,
            password=password,
            emp_id=emp_id,
            branchname=branch_id,
        )

        # Save Login details
        Login.objects.create(
            username=emp_id,
            password=password,
            utype='employee',
            employee_name=fullname
        )

        return redirect('employee')  # Redirect after saving, adjust URL as needed

    # Get all branches from the database to display in the form
    branches = Department.objects.all()
    jobRole = Jobrole.objects.all()

    return render(request, 'employee.html', {'branches': branches,'jobRole':jobRole})



def jobRole(request):
    if request.method == 'POST':

        jobRole = request.POST.get('jobRole')
        branchname = request.POST.get('branchname')

        Jobrole.objects.create(department=branchname,jobRole=jobRole)


        return redirect('jobRole')  # Adjust this redirect as needed
    branches = Jobrole.objects.all()  # Fetch all branch records from the database
    dept = Department.objects.all()  # Fetch all branch records from the database

    return render(request, 'jobRole.html', {'branches': branches,'dept':dept})





def edit_role(request, branch_id):
    # Get the branch object to edit
    branch = get_object_or_404(Jobrole, id=branch_id)

    # Handle form submission
    if request.method == 'POST':
        # Manually retrieve and update the branch fields
        branch.department = request.POST.get('branchname')
        branch.jobRole = request.POST.get('jobRole')

        branch.save()
        return redirect('jobRole')  # Redirect to the branch list after saving

    # Prepopulate form fields for the GET request
    branches = Jobrole.objects.all()  # Fetch all branch records from the database

    return render(request, 'edit_role.html', {'branch': branch,'branches':branches})

def view_certificate(request, id):
    employee = get_object_or_404(Employee, pk=id)
    return render(request, 'view_certificate.html', {'employee': employee})

    # Render the template with the employee data
    return render(request, 'employee_view.html', {'employee': employee})

def machine(request):
    if request.method == 'POST':

        machine = request.POST.get('machine')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')


        Machine.objects.create(machine=machine,description=description,machinephoto=photo)


        return redirect('machine')  # Adjust this redirect as needed
    machine = Machine.objects.all()  # Fetch all branch records from the database
    return render(request, 'machine.html', {'machine': machine})


def edit_machine(request, id):
    # Get the branch object to edit
    machine= get_object_or_404(Machine, id=id)

    # Handle form submission
    if request.method == 'POST':
        # Manually retrieve and update the branch fields
        machine.machine = request.POST.get('machine')
        machine.description = request.POST.get('description')

        machine.save()
        return redirect('machine')  # Redirect to the branch list after saving

    # Prepopulate form fields for the GET request

    return render(request, 'edit_machine.html', {'machine': machine})


def spareParts(request):
    if request.method == 'POST':
        machine_name = request.POST.get('machine')
        spare_parts_to_create = []

        # Iterate through each spare part entry in the form
        for i in range(1, len(request.POST) + 1):
            spare_part_name = request.POST.get(f'sparetpart_{i}')
            spare_part_no = request.POST.get(f'sparetpartNo_{i}')
            description = request.POST.get(f'description_{i}')
            photo = request.FILES.get(f'photo_{i}')  # Get the uploaded photo

            # Ensure that we have a spare part name and photo
            if spare_part_name and photo:
                # Get the list of sizes entered for this spare part
                sizes = request.POST.getlist(f'size_{i}[]')  # Multiple sizes can be entered as an array

                # If no sizes are entered, use None or skip this part
                if not sizes:
                    sizes = [None]  # If no sizes are provided, set as None

                # Create a spare part entry for each size (even if None)
                for size in sizes:
                    spare_part = Spareparts(
                        machine=machine_name,
                        sparepart=spare_part_name,
                        sparepartNo=spare_part_no,
                        description=description,
                        sparephoto=photo if photo else None,
                        sparepartsize=size  # Save the size (or None if no size)
                    )
                    spare_parts_to_create.append(spare_part)

        # Bulk save spare parts to reduce database queries
        if spare_parts_to_create:
            Spareparts.objects.bulk_create(spare_parts_to_create)

        return redirect('spareParts')  # Redirect to the spare parts list page

    # Get available machines for the select dropdown
    machines = Machine.objects.all()

    # Get all spare parts and items
    spareparts = Spareparts.objects.all()
    item = Item.objects.all()

    # Fetch all spare parts, including those without matching items
    matching_spare_parts = []
    for sparepart in spareparts:
        # Try to find matching items in the Item table by sparePart, sparePartNo, and sparepartsize
        matching_items = item.filter(
            sparePart=sparepart.sparepart,
            sparePartNo=sparepart.sparepartNo,
            sparepartsize=sparepart.sparepartsize
        )

        # If there are matching items, include them, otherwise set issuedqty to None
        if matching_items.exists():
            matching_spare_parts.append({
                'sparepart': sparepart,
                'matching_items': matching_items
            })
        else:
            matching_spare_parts.append({
                'sparepart': sparepart,
                'matching_items': None  # No matching items, so set issuedqty to None
            })

    return render(request, 'spareParts.html', {
        'machines': machines,
        'spareparts': spareparts,
        'matching_spare_parts': matching_spare_parts
    })




def edit_spare(request, id):
    # Get the Spareparts object to edit
    spareParts = get_object_or_404(Spareparts, id=id)

    # Initially, item is None (we will try to fetch the Item based on sparepartNo, sparepart, sparepartsize)
    try:
        item = Item.objects.get(
            sparePart=spareParts.sparepart,
            sparePartNo=spareParts.sparepartNo,
            sparepartsize=spareParts.sparepartsize
        )
    except Item.DoesNotExist:
        item = None  # Item does not exist; we may create it later

    # Handle form submission for POST requests
    if request.method == 'POST':
        # Update Spareparts model fields
        spareParts.machine = request.POST.get('machine')
        spareParts.sparetpart = request.POST.get('sparetpart')
        spareParts.sparepartNo = request.POST.get('sparepartNo')
        spareParts.description = request.POST.get('description')
        spareParts.sparepartsize = request.POST.get('sparepartsize')

        # Handle file upload for sparephoto
        if 'sparepartPhoto' in request.FILES:
            spareParts.sparephoto = request.FILES['sparepartPhoto']

        spareParts.save()  # Save changes to the Spareparts model

        # Extract form fields for the Item
        new_machine = request.POST.get('machine')
        new_sparepart = request.POST.get('sparetpart')
        new_sparepartNo = request.POST.get('sparepartNo')
        new_sparepartsize = request.POST.get('sparepartsize')

        if item:  # If Item exists (we fetched it by matching sparepart, sparepartNo, and sparepartsize)
            # Update the existing Item fields
            item.machineName = new_machine
            item.sparePart = new_sparepart
            item.sparePartNo = new_sparepartNo
            item.sparepartsize = new_sparepartsize
            item.save()  # Save the updated Item
        else:
            # If no matching Item exists, create a new Item
            try:
                Item.objects.create(
                    machineName=new_machine,
                    sparePart=new_sparepart,
                    sparePartNo=new_sparepartNo,
                    sparepartsize=new_sparepartsize,
                    issuedqty=0  # Default value for issuedqty, can be updated later
                )
            except IntegrityError as e:
                # Handle any database issues (like integrity constraints)
                print(f"Error creating Item: {e}")

        # Redirect to the list of spare parts after saving changes
        return redirect('spareParts')  # Adjust this to the correct view name for your case

    # Prepopulate form fields for the GET request
    machine = Machine.objects.all()  # Fetch all available machines to prepopulate the machine field

    return render(request, 'edit_spare.html', {
        'spareParts': spareParts,  # Pass the Spareparts object for prepopulation in the form
        'machine': machine,  # Pass available machines for the dropdown
        'item': item  # Pass the item if it was fetched by matching sparePart, sparePartNo, and sparepartsize
    })

def vendor(request):
    if request.method == 'POST':
        vendorName = request.POST.get('vendorName')
        companyName = request.POST.get('companyName')
        vendorAddress = request.POST.get('companyAddress')
        vendorPhone = request.POST.get('vendorPhone')
        companyPhone = request.POST.get('companyPhones')

        Vendor.objects.create(vendorName=vendorName,
                                  companyName=companyName,
                                  vendorAddress=vendorAddress,
                                  vendorPhone=vendorPhone,
                                  companyPhone=companyPhone
                                  )


        return redirect('vendor')  # Adjust this redirect as needed
    vendor = Vendor.objects.all()  # Fetch all branch records from the database

    return render(request, 'vendor.html', {'vendor': vendor})

def edit_vendor(request, id):
    # Get the branch object to edit
    branch = get_object_or_404(Vendor, id=id)

    # Handle form submission
    if request.method == 'POST':
        # Manually retrieve and update the branch fields
        branch.vendorName = request.POST.get('vendorName')
        branch.companyName = request.POST.get('companyName')
        branch.vendorAddress = request.POST.get('vendorAddress')
        branch.companyPhone = request.POST.get('companyPhone')
        branch.vendorAddress = request.POST.get('vendorAddress')

        branch.save()
        return redirect('vendor')  # Redirect to the branch list after saving

    # Prepopulate form fields for the GET request
    return render(request, 'edit_vendor.html', {'branch': branch})

from django.db.models import F

def entryHistory(request):
    if request.method == 'POST':
        print("POST Data:", request.POST)

        # Get the max entryId and increment it
        last_entryId = Stock.objects.aggregate(Max('entryId'))['entryId__max']
        entryId = int(last_entryId) + 1 if last_entryId else 1001
        con_id = str(entryId)

        # Get POST data
        vendorName = request.POST.get('vendor')
        vendorCompany = request.POST.get('vendorcompany')
        receivedBy = request.POST.get('employee')
        date = request.POST.get('date')
        description = request.POST.get('desc')

        # Get the list of array-based inputs
        department = request.POST.getlist('department[]')
        machines = request.POST.getlist('machine[]')
        spareParts = request.POST.getlist('sparetpart[]')
        sparePartNos = request.POST.getlist('sparetpartNo[]')
        sparepartsize = request.POST.getlist('sparepartsize[]')
        manufacturers = request.POST.getlist('manufacturer[]')
        rates = request.POST.getlist('rate[]')
        issuedQuantities = request.POST.getlist('issuedqty[]')
        remark = request.POST.getlist('remark[]')
        pos = request.POST.getlist('po[]')

        # List to hold new stock records
        stocks = []
        for i in range(len(machines)):
            if not machines[i] or not spareParts[i]:  # Skip invalid rows
                continue

            # Check if the sparePart, sparePartNo, and sparepartsize combination exists in the Item table
            existing_item = Item.objects.filter(
                sparePart=spareParts[i],
                sparePartNo=sparePartNos[i],
                sparepartsize=sparepartsize[i]
            ).first()

            if existing_item:
                # Update the existing record if it exists
                existing_item.machineName = machines[i]
                existing_item.issuedqty = F('issuedqty') + int(issuedQuantities[i])  # Increment the issued qty
                existing_item.save()
            else:
                # Create a new record if it doesn't exist
                Item.objects.create(
                    machineName=machines[i],
                    sparePart=spareParts[i],
                    sparePartNo=sparePartNos[i],
                    issuedqty=issuedQuantities[i],
                    sparepartsize=sparepartsize[i]
                )

            # Prepare stock entry for the Stock table
            stocks.append(Stock(
                vendorName=vendorName,
                vendorCompany=vendorCompany,
                description=description,
                receivedBy=receivedBy,
                date=date,
                department=department[i],
                machineName=machines[i],
                sparePart=spareParts[i],
                sparePartNo=sparePartNos[i],
                sparepartsize=sparepartsize[i],
                manufacturerName=manufacturers[i],
                rate=rates[i],
                issuedqty=issuedQuantities[i],
                remark=remark[i],
                po=pos[i],
                entryId=con_id
            ))

        # Bulk create the stock entries
        if stocks:
            Stock.objects.bulk_create(stocks)

        # Redirect to the same page after processing

    # Context for GET request
    machine = Machine.objects.all()
    department = Department.objects.all()
    spareParts = Spareparts.objects.values('sparepart').distinct()
    vendor = Vendor.objects.all()
    employee = Employee.objects.all()

    return render(request, 'entryHistory.html', {
        'machine': machine,
        'spareParts': spareParts,
        'vendor': vendor,
        'employee': employee,
        'department':department
    })


def get_vendor_details(request):
    name = request.GET.get('name', '')
    if name:
        consignor = Vendor.objects.filter(vendorName=name).first()
        if consignor:
            data = {
                'companyName': consignor.companyName,
            }
        else:
            data = {}
    else:
        data = {}

    return JsonResponse(data)


def get_spare_details(request):
    name = request.GET.get('name', '')
    if name:
        # Fetch all spare parts with the same name
        spareparts = Spareparts.objects.filter(sparepart=name)

        if spareparts.exists():
            # Fetch the sparepartNo (it should be the same for all rows of the same spare part)
            sparepartNo = spareparts.first().sparepartNo

            # Fetch all distinct sizes for the selected spare part
            sizes = spareparts.values_list('sparepartsize', flat=True).distinct()

            # Prepare the data to return
            data = {
                'sparepartNo': sparepartNo,
                'sparepartsize': list(sizes),  # Return the distinct sizes as a list
            }
        else:
            data = {}
    else:
        data = {}

    return JsonResponse(data)

def get_dept_emp(request):
    name = request.GET.get('name', '')  # Get department name from query string
    if name:
        # Filter employees based on the department name (branchname here)
        employees = Employee.objects.filter(branchname=name)

        if employees.exists():
            # Get distinct fullnames of employees in the selected department
            employee_names = employees.values_list('fullname', flat=True).distinct()

            # Prepare the data to send back as JSON
            data = {
                'fullname': list(employee_names),  # Return list of distinct fullnames
            }
        else:
            data = {'fullname': []}  # No employees found in this department
    else:
        data = {'fullname': []}  # No department selected

    return JsonResponse(data)

from datetime import datetime

from django.db.models import Q

def entryHistoryList(request):
    # Fetch date filter from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Filter entries by date if provided
    entries = Stock.objects.all()
    search_query = request.GET.get('search', '')  # Get the search term from the request

    if search_query:
        # Use Q objects to combine multiple fields with OR condition
        entries = entries.filter(
            Q(machineName__icontains=search_query) |
            Q(sparePart__icontains=search_query) |
            Q(sparePartNo__icontains=search_query) |
            Q(entryId__icontains=search_query) |
            Q(date__icontains=search_query)
        )

    if from_date:
        entries = entries.filter(date__gte=datetime.strptime(from_date, "%Y-%m-%d").date())
    if to_date:
        entries = entries.filter(date__lte=datetime.strptime(to_date, "%Y-%m-%d").date())

    # Group entries by entryId and calculate aggregate fields
    entries_summary = {}
    for entry in entries:
        entry_id = entry.entryId
        if entry_id not in entries_summary:
            # Initialize summary for each entryId
            entries_summary[entry_id] = {
                'date': entry.date,
                'po': entry.po,
                'machine_name': entry.machineName,
                'vendorCompany': entry.vendorCompany,
                'vendorName': entry.vendorName,
                'receivedBy': entry.receivedBy,
                'description': entry.description,

                'spare_parts': [],
                'total_issued_qty': 0,
            }

        # Fetch issuedQty from Item table by matching sparePart and sparePartSize
        matching_item = Item.objects.filter(
            sparePart=entry.sparePart, sparepartsize=entry.sparepartsize
        ).first()  # Assumes the first match is the correct one

        # If a matching Item is found, get the issuedQty, otherwise default to 0
        issued_qty = matching_item.issuedqty if matching_item else 0

        # Add spare part details for each entry, including issuedQty from Item table
        entries_summary[entry_id]['spare_parts'].append({
            'machineName': entry.machineName,
            'description': entry.description,
            'vendorCompany': entry.vendorCompany,
            'vendorName': entry.vendorName,
            'receivedBy': entry.receivedBy,
            'sparePart': entry.sparePart,
            'sparepartsize': entry.sparepartsize,
            'po': entry.po,
            'department': entry.department,
            'issuedQty': entry.issuedqty,
            'remark': entry.remark,
            'issued_qty': issued_qty,
        })

        # Update aggregate totals for issuedQty
        entries_summary[entry_id]['total_issued_qty'] += issued_qty

    return render(request, 'entryHistoryList.html', {'entries_summary': entries_summary})


def edit_entry(request, entry_id):
    # Fetch vendor and spare part details for the specified entry
    vendordeatils = Stock.objects.filter(entryId=entry_id).values('vendorName', 'vendorCompany', 'receivedBy').first()  # Use .first() to get a single result
    spare_part_details = Stock.objects.filter(entryId=entry_id).values(
        'vendorName', 'vendorCompany', 'receivedBy', 'machineName', 'sparePart',
        'sparePartNo', 'manufacturerName', 'rate', 'issuedqty', 'po'
    )

    if request.method == 'POST':
        # Handle vendor form submission
        vendor_name = request.POST.get('vendor')
        vendor_company = request.POST.get('vendorcompany')
        received_by = request.POST.get('employee')

        # Update vendor details in the Stock table (assuming only one entry per vendor)
        Stock.objects.filter(entryId=entry_id).update(
            vendorName=vendor_name, vendorCompany=vendor_company, receivedBy=received_by
        )

        # Iterate over the spare part details and update each spare part entry
        for i in range(len(request.POST.getlist('machine'))):
            machine = request.POST.getlist('machine')[i]
            spare_part = request.POST.getlist('sparetpart')[i]
            spare_part_no = request.POST.getlist('sparetpartNo')[i]
            manufacturer = request.POST.getlist('manufacturer')[i]
            rate = request.POST.getlist('rate')[i]
            issuedqty = request.POST.getlist('quantity')[i]
            po = request.POST.getlist('po')[i]

            # Update or create entries in Stock for each spare part
            Stock.objects.update_or_create(
                entryId=entry_id, sparePart=spare_part, defaults={
                    'machineName': machine, 'sparePartNo': spare_part_no,
                    'manufacturerName': manufacturer, 'rate': rate,
                    'issuedqty': issuedqty, 'po': po
                }
            )

        # Redirect to entry history list after updating the details
        return redirect('entryHistoryList')

    machine = Machine.objects.all()
    spareParts = Spareparts.objects.all()
    vendor = Vendor.objects.all()
    employee = Employee.objects.all()

    return render(request, 'edit_entry.html', {
        'entry_id': entry_id,
        'spare_part_details': spare_part_details,
        'vendordeatils': vendordeatils,
        'machine':machine,
        'spareParts':spareParts,
        'vendor':vendor,
        'employee':employee

    })

logger = logging.getLogger(__name__)


def stockToDepartment(request):
    """Render the main template with all items and handle form submission."""
    spareParts = Spareparts.objects.values('sparepart').distinct()
    department = Department.objects.all()
    machine = Machine.objects.all()
    error_message = None  # Initialize error_message

    if request.method == "POST":
        try:
            now = datetime.now()
            con_date = now.strftime("%Y-%m-%d")
            sparetpart = request.POST.get('sparetpart')
            machine = request.POST.get('machine')
            part_no = request.POST.get('sparetpartNo')
            sparepartsize = request.POST.get('sparepartsize')
            receivedBy = request.POST.get('name')
            qty = int(request.POST.get('quantity', 0))
            issuedqty = int(request.POST.get('issuedqty', 0))
            balancedqty = int(request.POST.get('balancedqty', 0))
            department = request.POST.get('department')
            remark = request.POST.get('remark')

            # Check for missing fields
            if not all([sparetpart, part_no, qty, department]):
                error_message = "All fields are required."
                return render(request, "stockToDepartment.html", {
                    "stock": Spareparts,
                    "department": department,
                    'machine': machine,
                    'error_message': error_message
                })

            # Check for item existence in Godown
            godown_items = Item.objects.filter(sparePart=sparetpart, sparePartNo=part_no,sparepartsize=sparepartsize)
            logger.debug(f"Found {godown_items.count()} items in the godown")

            if godown_items.exists():
                godown_item = godown_items.first()

                # Check if there is enough quantity in the godown
                if godown_item.issuedqty >= qty:
                    # Update the godown item
                    godown_item.issuedqty -= qty
                    godown_item.save()

                    # Check if the record already exists in Deptstock table
                    deptstock_item = Deptstock.objects.filter(
                        sparePart=sparetpart,
                        sparePartNo=part_no,
                        department=department,
                        sparepartsize=sparepartsize
                    ).first()

                    if deptstock_item:
                        # If the record exists, update the quantity and date
                        deptstock_item.qty += qty
                        deptstock_item.date = con_date
                        deptstock_item.save()
                    else:
                        # If the record doesn't exist, create a new entry
                        Deptstock.objects.create(
                            machineName=machine,
                            sparePart=sparetpart,
                            sparePartNo=part_no,
                            sparepartsize=sparepartsize,
                            qty=qty,
                            department=department,
                            date=con_date
                        )

                    # Save data to StocktoDept table
                    godown_to_branch = StocktoDept(
                        machineName=machine,
                        sparePart=sparetpart,
                        sparePartNo=part_no,
                        qty=qty,
                        issuedqty=issuedqty,
                        balancedqty=balancedqty,
                        department=department,
                        date=con_date,
                        receivedBy=receivedBy,
                        sparepartsize=sparepartsize,
                        remark=remark,

                    )
                    godown_to_branch.save()

                    return redirect('stockToDepartment')  # Redirect to the same page for new form submission

                else:
                    error_message = "Insufficient quantity in Godown!"
            else:
                error_message = "Item not found in Godown!"
        except Exception as e:
            logger.error("Error processing form data: %s", e)
            error_message = "Server error."

        # If there is an error, pass it to the template
        return render(request, "stockToDepartment.html", {
            "spareParts": spareParts,
            "department": department,
            'machine': machine,
            'error_message': error_message
        })

    return render(request, "stockToDepartment.html", {
        "spareParts": spareParts,
        "department": department,
        'machine': machine
    })

def stockToDepartmentList(request):
    # Get all StocktoDept objects
    stock = StocktoDept.objects.all()

    # Get search query from request
    search_query = request.GET.get('search', '')  # Get the search term from the request

    # If a search query is provided, filter the stock queryset based on the search query
    if search_query:
        stock = stock.filter(
            Q(machineName__icontains=search_query) |
            Q(sparePart__icontains=search_query) |
            Q(sparePartNo__icontains=search_query) |
            Q(date__icontains=search_query)
        )

    # List to store the final data including matched qty
    deptstocks = []

    # Iterate over each StocktoDept object
    for s in stock:
        # Filter Deptstock records matching the criteria
        deptstock = Deptstock.objects.filter(
            sparePart=s.sparePart,
            sparePartNo=s.sparePartNo,
            sparepartsize=s.sparepartsize,
            department=s.department
        ).first()  # We get the first match since we're assuming a 1-to-1 match for qty.

        # If a matching Deptstock is found, include its qty
        if deptstock:
            deptstocks.append({
                'sparePart': s.sparePart,
                'sparePartNo': s.sparePartNo,
                'sparepartsize': s.sparepartsize,
                'department': s.department,
                'issuedQty': s.issuedqty,
                'balanceQty': s.balancedqty,
                'receivedqty': s.qty,
                'date': s.date,
                'remark': s.remark,
                'machineName': s.machineName,
                'receivedBy': s.receivedBy,
                'qty': deptstock.qty  # Directly use the qty from Deptstock
            })
        else:
            # If no matching Deptstock is found, include default values or leave empty for qty
            deptstocks.append({
                'sparePart': s.sparePart,
                'sparePartNo': s.sparePartNo,
                'sparepartsize': s.sparepartsize,
                'department': s.department,
                'issuedQty': s.issuedQty,
                'balanceQty': s.balanceQty,
                'receivedqty': s.qty,
                'date': s.date,
                'remark': s.remark,
                'machineName': s.machineName,
                'receivedBy': s.receivedBy,
                'qty': 0  # No match, set qty to 0
            })

    # Pass the data to the template
    return render(request, 'stockToDepartmentList.html', {'deptstocks': deptstocks})

def sparePartStock(request):
    spartpart = Spareparts.objects.all()  # Get all spare parts
    spare = Stock.objects.all()  # Get all stock records

    # Check if a search term is provided in the GET request
    search_term = request.GET.get('search', '').strip()  # Get the search term (default to empty string if not present)

    # If a search term is provided, filter spare parts and stock based on the search term
    if search_term:
        # Use Q objects to filter on multiple fields (sparePart and sparePartNo)
        spare = spare.filter(
            Q(sparePart__icontains=search_term) |
            Q(sparePartNo__icontains=search_term)
        )

    # Group the stock by spare part and calculate the total quantity for each spare part
    grouped_stock = spare.values('sparePart').annotate(total_stock=Sum('issuedqty'))

    return render(request, 'sparePartStock.html', {
        'spartpart': spartpart,
        'grouped_stock': grouped_stock,
        'search_term': search_term,  # Pass the search term back to the template
    })

from django.utils.dateparse import parse_date


def viewSpare(request, name):
    # Capture the 'from_date' and 'to_date' from the POST request
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')

    # Convert the dates to proper format if they exist
    if from_date:
        from_date = parse_date(from_date)
    if to_date:
        to_date = parse_date(to_date)

    # Get all stock items that match the spare part name (returns a QuerySet)
    spare = Stock.objects.filter(sparePart=name)

    # If dates are provided, filter the spare items by the date range
    if from_date and to_date:
        spare = spare.filter(date__range=[from_date, to_date])
    elif from_date:
        spare = spare.filter(date__gte=from_date)
    elif to_date:
        spare = spare.filter(date__lte=to_date)

    # Calculate the total issued quantity (sum of issuedqty)
    total_issued_qty = spare.aggregate(Sum('issuedqty'))['issuedqty__sum'] or 0  # Default to 0 if no results

    if spare.exists():
        # Get the sparePartNo from the first item in the spare queryset
        sparepart = spare.first().sparePartNo
        # Get all Spareparts that match the sparePartNo
        images = Spareparts.objects.filter(sparepartNo=sparepart)
    else:
        spare = None  # No spare part found
        images = None  # No matching Spareparts

    # Pass the spare items and total issued quantity to the template
    return render(request, 'viewSpare.html', {
        'spare': spare,
        'images': images,  # Pass all matching Spareparts
        'total_issued_qty': total_issued_qty,
        'from_date': from_date,
        'to_date': to_date,
    })

logger = logging.getLogger(__name__)

def departmentTodepartment(request):
    """Render the main template with all items and handle form submission."""
    spareParts = Spareparts.objects.values('sparepart').distinct()
    department = Department.objects.all()
    machine = Machine.objects.all()
    error_message = None  # Initialize error_message

    if request.method == "POST":
        try:
            now = datetime.now()
            con_date = now.strftime("%Y-%m-%d")
            sparetpart = request.POST.get('sparetpart')
            machine = request.POST.get('machine')
            part_no = request.POST.get('sparetpartNo')
            sparepartsize = request.POST.get('sparepartsize')
            qty = int(request.POST.get('quantity', 0))
            issuedqty = int(request.POST.get('issuedqty', 0))
            balancedqty = int(request.POST.get('balancedqty', 0))
            fromdepartment = request.POST.get('fromdepartment')
            todepartment = request.POST.get('todepartment')
            receivedBy = request.POST.get('fromname')
            receivedFrom = request.POST.get('toname')
            remark = request.POST.get('remark')

            # Log the received form data
            logger.debug(f"Form data received: sparetpart={sparetpart}, part_no={part_no}, qty={qty}, "
                         f"fromdepartment={fromdepartment}, todepartment={todepartment}, machine={machine}")

            # Check if any required fields are missing
            if not all([sparetpart, part_no, qty, fromdepartment, todepartment]):
                error_message = "All fields are required."
                logger.error(f"Error: {error_message}. Missing fields: "
                             f"sparetpart={sparetpart}, part_no={part_no}, qty={qty}, "
                             f"fromdepartment={fromdepartment}, todepartment={todepartment}")
                return render(request, "departmentTodepartment.html", {
                    "spareParts": spareParts,
                    "department": department,
                    'machine': machine,
                    'error_message': error_message
                })

            # Check for the item in the fromdepartment
            godown_items = Deptstock.objects.filter(sparePart=sparetpart, sparePartNo=part_no, department=fromdepartment,sparepartsize=sparepartsize)
            logger.debug(f"Found {godown_items.count()} items in the fromdepartment")

            if godown_items.exists():
                godown_item = godown_items.first()

                # Ensure there's enough stock in the fromdepartment
                if godown_item.qty >= qty:
                    godown_item.qty -= qty
                    godown_item.save()

                    # Check if the item already exists in the todepartment
                    to_dept_item = Deptstock.objects.filter(sparePart=sparetpart, sparePartNo=part_no, department=todepartment,sparepartsize=sparepartsize).first()

                    if to_dept_item:
                        # If the record exists in todepartment, update it
                        to_dept_item.qty += qty
                        to_dept_item.date = con_date
                        to_dept_item.save()
                    else:
                        # If no record exists, create a new entry in the todepartment
                        Deptstock.objects.create(
                            sparePart=sparetpart,
                            sparePartNo=part_no,
                            sparepartsize=sparepartsize,
                            qty=qty,
                            department=todepartment,
                            date=con_date,
                            machineName=machine
                        )

                    # Record the transfer in DepttoDept table
                    godown_to_branch = DepttoDept(
                        machineName=machine,
                        sparePart=sparetpart,
                        sparePartNo=part_no,
                        qty=qty,
                        fromdepartment=fromdepartment,
                        todepartment=todepartment,
                        date=con_date,
                        receivedFrom=receivedFrom,
                        receivedBy=receivedBy,
                        issuedqty=issuedqty,
                        balanceqty=balancedqty,
                        remark=remark,
                        sparepartsize=sparepartsize,

                    )
                    godown_to_branch.save()

                    return redirect('departmentTodepartment')  # Redirect to refresh the page or target another view

                else:
                    error_message = "Insufficient quantity in the fromdepartment!"
                    logger.error(f"Error: {error_message}. Available qty: {godown_item.qty}, requested qty: {qty}")

            else:
                error_message = "Item not found in the fromdepartment!"
                logger.error(f"Error: {error_message}. SparePart: {sparetpart}, SparePartNo: {part_no}, FromDepartment: {fromdepartment}")

        except Exception as e:
            logger.error("Error processing form data: %s", e)
            error_message = "Server error."

        # If there is an error, pass it to the template
        return render(request, "departmentTodepartment.html", {
            "spareParts": spareParts,
            "department": department,
            'machine': machine,
            'error_message': error_message
        })

    return render(request, "departmentTodepartment.html", {
        "spareParts": spareParts,
        "department": department,
        'machine': machine
    })


from django.db.models import Q

def deptTodeptList(request):
    # Get all DepttoDept objects
    stock = DepttoDept.objects.all()

    # Get search query from request
    search_query = request.GET.get('search', '')  # Get the search term from the request

    # If a search query is provided, filter the stock queryset based on the search query
    if search_query:
        stock = stock.filter(
            Q(machineName__icontains=search_query) |
            Q(sparePart__icontains=search_query) |
            Q(sparePartNo__icontains=search_query) |
            Q(date__icontains=search_query)
        )

    # List to store the final data including matched qty for both departments
    deptstocks = []

    # Iterate over each DepttoDept object
    for s in stock:
        # Match Deptstock records for 'fromDepartment'
        deptstock_from = Deptstock.objects.filter(
            sparePart=s.sparePart,
            sparePartNo=s.sparePartNo,
            sparepartsize=s.sparepartsize,
            department=s.fromdepartment  # matching with 'fromDepartment'
        ).first()  # Get the first match for 'fromDepartment'

        # Match Deptstock records for 'toDepartment'
        deptstock_to = Deptstock.objects.filter(
            sparePart=s.sparePart,
            sparePartNo=s.sparePartNo,
            sparepartsize=s.sparepartsize,
            department=s.todepartment  # matching with 'toDepartment'
        ).first()  # Get the first match for 'toDepartment'

        # If a matching Deptstock is found for 'fromDepartment', get its qty
        qty_from = deptstock_from.qty if deptstock_from else 0

        # If a matching Deptstock is found for 'toDepartment', get its qty
        qty_to = deptstock_to.qty if deptstock_to else 0

        # Add both fromDepartment and toDepartment data with their respective qty
        deptstocks.append({
            'sparePart': s.sparePart,
            'sparePartNo': s.sparePartNo,
            'sparepartsize': s.sparepartsize,
            'fromdepartment': s.fromdepartment,
            'todepartment': s.todepartment,
            'issuedqty': s.issuedqty,
            'qty': s.qty,
            'date': s.date,
            'receivedBy': s.receivedBy,
            'receivedFrom': s.receivedFrom,
            'remark': s.remark,
            'machineName': s.machineName,
            'qty_from': qty_from,  # Quantity for 'fromDepartment'
            'qty_to': qty_to,      # Quantity for 'toDepartment'
        })

    # Pass the data to the template
    return render(request, 'deptTodeptList.html', {'deptstocks': deptstocks})

def deptStock(request):
    stock = Deptstock.objects.all()  # Get all stock records

    search_query = request.GET.get('search', '')  # Get the search term from the request

    if search_query:
        # Use Q objects to combine multiple fields with OR condition
        stock = stock.filter(
            Q(machineName__icontains=search_query) |
            Q(sparePart__icontains=search_query) |
            Q(sparePartNo__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(date__icontains=search_query)
        )
    return render(request,'deptStock.html',{'stock':stock})

def spareStock(request):
    spartpart = Spareparts.objects.all()  # Get all spare parts
    spare = StocktoDept.objects.all()  # Get all stock records

    # Check if a search term is provided in the GET request
    search_term = request.GET.get('search', '').strip()  # Get the search term (default to empty string if not present)

    # If a search term is provided, filter spare parts and stock based on the search term
    if search_term:
        # Use Q objects to filter on multiple fields (sparePart and sparePartNo)
        spare = spare.filter(
            Q(sparePart__icontains=search_term) |
            Q(sparePartNo__icontains=search_term)
        )

    # Group the stock by spare part and calculate the total quantity for each spare part
    grouped_stock = spare.values('sparePart').annotate(total_stock=Sum('qty'))

    return render(request, 'spareStock.html', {
        'spartpart': spartpart,
        'grouped_stock': grouped_stock,
        'search_term': search_term,  # Pass the search term back to the template
    })

def viewspareStock(request, name):
    # Capture the 'from_date' and 'to_date' from the POST request
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')

    # Convert the dates to proper format if they exist
    if from_date:
        from_date = parse_date(from_date)
    if to_date:
        to_date = parse_date(to_date)

    # Get all stock items that match the spare part name (returns a QuerySet)
    spare = StocktoDept.objects.filter(sparePart=name)

    # If dates are provided, filter the spare items by the date range
    if from_date and to_date:
        spare = spare.filter(date__range=[from_date, to_date])
    elif from_date:
        spare = spare.filter(date__gte=from_date)
    elif to_date:
        spare = spare.filter(date__lte=to_date)

    # Calculate the total issued quantity (sum of issuedqty)
    total_issued_qty = spare.aggregate(Sum('qty'))['qty__sum'] or 0  # Default to 0 if no results

    if spare.exists():
        # Get the sparePartNo from the first item in the spare queryset
        sparepart = spare.first().sparePartNo
        # Get all Spareparts that match the sparePartNo
        images = Spareparts.objects.filter(sparepartNo=sparepart)
    else:
        spare = None  # No spare part found
        images = None  # No matching Spareparts

    # Pass the spare items and total issued quantity to the template
    return render(request, 'viewspareStock.html', {
        'spare': spare,
        'images': images,  # Pass all matching Spareparts
        'total_issued_qty': total_issued_qty,
        'from_date': from_date,
        'to_date': to_date,
    })


def deptspareStock(request):
    spartpart = Spareparts.objects.all()  # Get all spare parts
    spare = DepttoDept.objects.all()  # Get all stock records

    # Check if a search term is provided in the GET request
    search_term = request.GET.get('search', '').strip()  # Get the search term (default to empty string if not present)

    # If a search term is provided, filter spare parts and stock based on the search term
    if search_term:
        # Use Q objects to filter on multiple fields (sparePart and sparePartNo)
        spare = spare.filter(
            Q(sparePart__icontains=search_term) |
            Q(sparePartNo__icontains=search_term)
        )

    # Group the stock by spare part and calculate the total quantity for each spare part
    grouped_stock = spare.values('sparePart').annotate(total_stock=Sum('qty'))

    return render(request, 'deptspareStock.html', {
        'spartpart': spartpart,
        'grouped_stock': grouped_stock,
        'search_term': search_term,  # Pass the search term back to the template
    })

def viewdeptspareStock(request, name):
    # Capture the 'from_date' and 'to_date' from the POST request
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')

    # Convert the dates to proper format if they exist
    if from_date:
        from_date = parse_date(from_date)
    if to_date:
        to_date = parse_date(to_date)

    # Get all stock items that match the spare part name (returns a QuerySet)
    spare = DepttoDept.objects.filter(sparePart=name)

    # If dates are provided, filter the spare items by the date range
    if from_date and to_date:
        spare = spare.filter(date__range=[from_date, to_date])
    elif from_date:
        spare = spare.filter(date__gte=from_date)
    elif to_date:
        spare = spare.filter(date__lte=to_date)

    # Calculate the total issued quantity (sum of issuedqty)
    total_issued_qty = spare.aggregate(Sum('qty'))['qty__sum'] or 0  # Default to 0 if no results

    if spare.exists():
        # Get the sparePartNo from the first item in the spare queryset
        sparepart = spare.first().sparePartNo
        # Get all Spareparts that match the sparePartNo
        images = Spareparts.objects.filter(sparepartNo=sparepart)
    else:
        spare = None  # No spare part found
        images = None  # No matching Spareparts

    # Pass the spare items and total issued quantity to the template
    return render(request, 'viewdeptspareStock.html', {
        'spare': spare,
        'images': images,  # Pass all matching Spareparts
        'total_issued_qty': total_issued_qty,
        'from_date': from_date,
        'to_date': to_date,
    })


def inventory_inward_print(request, entry_id):
    # Fetch stock items based on entry_id
    stock_items = Stock.objects.filter(entryId=entry_id)

    # Fetch the first stock item (you may want to check all items for vendors if needed)
    stock_item = stock_items.first()  # Replace with specific query if needed
    vendor = None  # Default value in case no vendor is found

    if stock_item:
        vendor_name = stock_item.vendorName

        # Fetch details from the Vendor table where vendorName matches
        vendor = Vendor.objects.filter(vendorName=vendor_name).first()  # Use .get() if you expect a single match
        if vendor:
            print(
                f"Vendor Details: {vendor.vendorName}, {vendor.companyName}, {vendor.vendorAddress}, {vendor.companyPhone}, {vendor.vendorPhone}")
        else:
            print("No vendor found matching the vendorName.")
    else:
        print("No stock item found.")

    # Assuming we only need the first item for additional stock details (adjust as necessary)
    stock = stock_items.first()

    # Render the template with the fetched details
    return render(request, 'printEntry.html', {
        'stock_items': stock_items,  # All stock items for the entry
        'vendordetails': vendor,  # Vendor object to access all vendor fields
        'stock': stock,  # First stock item for additional details
        'signature_url': '/path/to/signature/image.jpg'  # Adjust as needed
    })

def printEntryBill(request, entry_id):
    # Fetch stock items based on entry_id
    stock_items = Stock.objects.filter(entryId=entry_id)

    # Fetch the first stock item (you may want to check all items for vendors if needed)
    stock_item = stock_items.first()  # Replace with specific query if needed
    vendor = None  # Default value in case no vendor is found

    if stock_item:
        vendor_name = stock_item.vendorName

        # Fetch details from the Vendor table where vendorName matches
        vendor = Vendor.objects.filter(vendorName=vendor_name).first()  # Use .get() if you expect a single match
        if vendor:
            print(
                f"Vendor Details: {vendor.vendorName}, {vendor.companyName}, {vendor.vendorAddress}, {vendor.companyPhone}, {vendor.vendorPhone}")
        else:
            print("No vendor found matching the vendorName.")
    else:
        print("No stock item found.")

    # Assuming we only need the first item for additional stock details (adjust as necessary)
    stock = stock_items.first()

    # Render the template with the fetched details
    return render(request, 'printEntryBill.html', {
        'stock_items': stock_items,  # All stock items for the entry
        'vendordetails': vendor,  # Vendor object to access all vendor fields
        'stock': stock,  # First stock item for additional details
        'signature_url': '/path/to/signature/image.jpg'  # Adjust as needed
    })
