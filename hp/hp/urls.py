"""hp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from hp_app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('',views.index,name='index'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('emp_dashboard',views.emp_dashboard,name='emp_dashboard'),

    path('branch',views.branch,name='branch'),
    path('edit_branch/<int:branch_id>/', views.edit_branch, name='edit_branch'),

    path('generate_employee_id',views.generate_employee_id,name='generate_employee_id'),

    path('employee',views.employee,name='employee'),
    path('emp_list',views.emp_list,name='emp_list'),
    path('edit_employee/edit/<int:id>/', views.edit_employee, name='edit_employee'),
    path('view_certificate/<int:id>/', views.view_certificate, name='view_certificate'),


    path('jobRole',views.jobRole,name='jobRole'),
    path('edit_role/<int:branch_id>/', views.edit_role, name='edit_role'),

    path('machine',views.machine,name='machine'),
    path('edit_machine/<int:id>',views.edit_machine,name='edit_machine'),

    path('spareParts',views.spareParts,name='spareParts'),
    path('edit_spare/<int:id>',views.edit_spare,name='edit_spare'),

    path('vendor', views.vendor, name='vendor'),
    path('edit_vendor/<int:id>', views.edit_vendor, name='edit_vendor'),

    path('entryHistory',views.entryHistory,name='entryHistory'),
    path('get_vendor_details',views.get_vendor_details,name='get_vendor_details'),
    path('get_spare_details',views.get_spare_details,name='get_spare_details'),
    path('get_dept_emp',views.get_dept_emp,name='get_dept_emp'),

    path('entryHistoryList',views.entryHistoryList,name='entryHistoryList'),
    path('edit_entry/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('sparePartStock', views.sparePartStock, name='sparePartStock'),
    path('viewSpare/<str:name>/', views.viewSpare, name='viewSpare'),

    path('stockToDepartment', views.stockToDepartment, name='stockToDepartment'),
    path('stockToDepartmentList', views.stockToDepartmentList, name='stockToDepartmentList'),

    path('departmentTodepartment', views.departmentTodepartment, name='departmentTodepartment'),
    path('deptTodeptList', views.deptTodeptList, name='deptTodeptList'),

    path('deptStock', views.deptStock, name='deptStock'),

    path('spareStock', views.spareStock, name='spareStock'),
    path('viewspareStock/<str:name>/', views.viewspareStock, name='viewspareStock'),

    path('deptspareStock', views.deptspareStock, name='deptspareStock'),
    path('viewdeptspareStock/<str:name>/', views.viewdeptspareStock, name='viewdeptspareStock'),
    path('inventory_inward_print/<int:entry_id>/', views.inventory_inward_print, name='inventory_inward_print'),
    path('printEntry/<int:entry_id>/', views.printEntryBill, name='printEntryBill'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
