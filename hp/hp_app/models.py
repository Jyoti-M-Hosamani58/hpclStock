from idlelib.pyparse import trans

from django.db import models

class Department(models.Model):
    department = models.CharField(max_length=100)

class Jobrole(models.Model):
    department = models.CharField(max_length=100)
    jobRole = models.CharField(max_length=100)

class Machine(models.Model):
    machine = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    machinephoto = models.ImageField(upload_to='photos/', blank=True, null=True)

class Spareparts(models.Model):
    machine = models.CharField(max_length=255)
    sparepart = models.CharField(max_length=255)
    sparepartsize = models.CharField(max_length=255,null=True)
    sparepartNo = models.CharField(max_length=255, null=True)
    description = models.TextField()
    sparephoto = models.ImageField(upload_to='spareparts/', null=True, blank=True)

    def __str__(self):
        return self.sparepart


class Login(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    utype=models.CharField(max_length=50)
    employee_name = models.CharField(max_length=50)
    branchname = models.CharField(max_length=50)




class Employee(models.Model):
    fullname = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    dob=models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    nationality = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    Taluk = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    adhar = models.CharField(max_length=50)
    pancard = models.CharField(max_length=50)
    jrole = models.CharField(max_length=50)
    doj = models.CharField(max_length=50)
    pf = models.CharField(max_length=50)
    adhar_doc = models.FileField(upload_to='pdfs/')
    pan_doc = models.FileField(upload_to='pdfs/')
    bank_doc = models.FileField(upload_to='pdfs/')
    exp_doc = models.FileField(upload_to='pdfs/')
    tenthpass = models.CharField(max_length=50)
    tenth_percentage = models.CharField(max_length=50)
    twelfth_pass = models.CharField(max_length=50)
    twelfth_percentage = models.CharField(max_length=50)
    degree = models.CharField(max_length=50)
    degreepass = models.CharField(max_length=50)
    degree_percentage = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    emp_id = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    branchname = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)


class Material(models.Model):
    material = models.CharField(max_length=500, null=True)
    description = models.CharField(max_length=500,null=True)




class Vendor(models.Model):
    vendorName = models.CharField(max_length=500,null=True)
    companyName = models.CharField(max_length=500, null=True)
    vendorAddress = models.CharField(max_length=500,null=True)
    vendorPhone = models.CharField(max_length=500, null=True)
    companyPhone = models.CharField(max_length=500, null=True)


class Stock(models.Model):
    vendorName = models.CharField(max_length=100)
    vendorCompany = models.CharField(max_length=500,null=True)
    receivedBy = models.CharField(max_length=100)
    date = models.DateField(null=True)
    machineName = models.CharField(max_length=100)
    sparePart=models.CharField(max_length=100)
    sparePartNo=models.CharField(max_length=100,null=True)
    manufacturerName=models.CharField(max_length=100)
    rate=models.FloatField(null=True)
    issuedqty=models.IntegerField(null=True)
    po=models.CharField(max_length=100,null=True)
    entryId=models.CharField(max_length=100,null=True)
    description=models.CharField(max_length=100,null=True)
    remark=models.CharField(max_length=100,null=True)
    sparepartsize = models.CharField(max_length=255,null=True)
    department = models.CharField(max_length=255,null=True)


class Item(models.Model):
    machineName = models.CharField(max_length=100)
    sparePart = models.CharField(max_length=100)
    sparePartNo = models.CharField(max_length=100, null=True)
    issuedqty = models.IntegerField(null=True)
    sparepartsize = models.CharField(max_length=255,null=True)




class StocktoDept(models.Model):
    machineName = models.CharField(max_length=500,null=True)
    sparePart = models.CharField(max_length=500, null=True)
    sparePartNo = models.CharField(max_length=500, null=True)
    sparepartsize = models.CharField(max_length=500, null=True)
    receivedBy = models.CharField(max_length=500, null=True)
    qty = models.IntegerField(null=True)
    department = models.CharField(max_length=500,null=True)
    date = models.DateField(null=True)
    issuedqty = models.CharField(max_length=500,null=True)
    balancedqty = models.CharField(max_length=500,null=True)
    remark = models.CharField(max_length=500,null=True)

class Deptstock(models.Model):
    machineName = models.CharField(max_length=500,null=True)
    sparePart = models.CharField(max_length=500, null=True)
    sparePartNo = models.CharField(max_length=500, null=True)
    sparepartsize = models.CharField(max_length=500, null=True)
    qty = models.IntegerField(null=True)
    department = models.CharField(max_length=500,null=True)
    date = models.DateField(null=True)

class DepttoDept(models.Model):
    machineName = models.CharField(max_length=500,null=True)
    sparePart = models.CharField(max_length=500, null=True)
    sparePartNo = models.CharField(max_length=500, null=True)
    sparepartsize = models.CharField(max_length=500, null=True)
    qty = models.IntegerField(null=True)
    issuedqty = models.IntegerField(null=True)
    balanceqty = models.IntegerField(null=True)
    fromdepartment = models.CharField(max_length=500,null=True)
    todepartment = models.CharField(max_length=500,null=True)
    receivedBy = models.CharField(max_length=500,null=True)
    receivedFrom = models.CharField(max_length=500,null=True)
    remark = models.CharField(max_length=500,null=True)
    date = models.DateField(null=True)
