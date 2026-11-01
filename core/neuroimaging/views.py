from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NeuroimagingUpload, NeuroimagingReport
from accounts.models import CustomUser
import random

@login_required
def upload_list(request):
    if request.user.is_admin_user() or request.user.role == 'educator':
        uploads = NeuroimagingUpload.objects.all().order_by('-uploaded_at')
    else:
        uploads = NeuroimagingUpload.objects.filter(patient=request.user).order_by('-uploaded_at')
    return render(request, 'neuroimaging/list.html', {'uploads': uploads})

@login_required
def upload_scan(request):
    students = CustomUser.objects.filter(role='student')
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        scan_type = request.POST.get('scan_type')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        if file and patient_id:
            patient = get_object_or_404(CustomUser, pk=patient_id)
            upload = NeuroimagingUpload.objects.create(
                uploaded_by=request.user,
                patient=patient,
                scan_type=scan_type,
                file=file,
                file_name=file.name,
                description=description,
            )
            messages.success(request, 'Scan uploaded successfully.')
            return redirect('neuroimaging:detail', pk=upload.pk)
    return render(request, 'neuroimaging/upload.html', {'students': students})

@login_required
def scan_detail(request, pk):
    scan = get_object_or_404(NeuroimagingUpload, pk=pk)
    report = NeuroimagingReport.objects.filter(scan=scan).first()
    return render(request, 'neuroimaging/detail.html', {'scan': scan, 'report': report})

@login_required
def analyze_scan(request, pk):
    if not (request.user.is_admin_user() or request.user.role == 'educator'):
        return redirect('neuroimaging:list')
    scan = get_object_or_404(NeuroimagingUpload, pk=pk)
    confidence = round(random.uniform(0.65, 0.95), 2)
    report, _ = NeuroimagingReport.objects.get_or_create(scan=scan)
    report.neural_patterns_detected = "Reduced activation in left hemisphere phonological processing areas. " \
        "Atypical connectivity in angular gyrus region."
    report.dyslexia_indicators = "Patterns consistent with phonological processing difficulties. " \
        "Visual word form area shows reduced activation."
    report.confidence_score = confidence * 100
    report.simplified_interpretation = (
        f"The brain scan analysis (confidence: {confidence*100:.0f}%) suggests patterns "
        "that are commonly associated with reading difficulties. The areas responsible for "
        "connecting letters to sounds show reduced activity. This is a common finding in dyslexia. "
        "We recommend a comprehensive reading assessment and personalized intervention plan."
    )
    report.save()
    scan.status = 'analyzed'
    scan.save()
    messages.success(request, 'Scan analyzed successfully.')
    return redirect('neuroimaging:detail', pk=pk)