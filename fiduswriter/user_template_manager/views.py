from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from document.models import DocumentTemplate
from style.models import CitationStyle
from document.helpers.serializers import PythonWithURLSerializer


@login_required
def list(request):
    response = {}
    status = 405
    if request.is_ajax() and request.method == 'POST':
        status = 200
        doc_templates = DocumentTemplate.objects.filter(
            Q(user=request.user) | Q(user=None)
        )
        date_format = '%Y-%m-%d'
        response['document_templates'] = [
            {
                'id': obj.id,
                'title': obj.title,
                'is_owner': (obj.user is not None),
                'added': obj.added.strftime(date_format),
                'updated': obj.updated.strftime(date_format)
            } for obj in doc_templates
        ]
    return JsonResponse(
        response,
        status=status
    )


@login_required
def get(request):
    if not request.is_ajax() or request.method != 'POST':
        return JsonResponse({}, status=405)
    id = request.POST['id']
    if id == 0:
        doc_template = DocumentTemplate()
        doc_template.user = request.user
        doc_template.save()
        status = 201
    else:
        doc_template = DocumentTemplate.objects.filter(
            Q(id=id),
            Q(user=request.user) | Q(user=None)
        ).first()
        status = 200
    if doc_template is None:
        return JsonResponse({}, status=405)
    serializer = PythonWithURLSerializer()
    export_templates = serializer.serialize(
        doc_template.exporttemplate_set.all()
    )
    document_styles = serializer.serialize(
        doc_template.documentstyle_set.all(),
        use_natural_foreign_keys=True
    )
    citation_styles = serializer.serialize(
        CitationStyle.objects.all()
    )
    response = {
        'template': {
            'id': doc_template.id,
            'title': doc_template.title,
            'definition': doc_template.definition,
            'definition_hash': doc_template.definition_hash,
            'export_templates': export_templates,
            'document_styles': document_styles,
            'citation_styles': [
                f.id for f in doc_template.citation_styles.all()
            ],
        },
        'citation_styles': citation_styles,
    }
    return JsonResponse(
        response,
        status=status
    )


@login_required
def copy(request):
    if not request.is_ajax() or request.method != 'POST':
        return JsonResponse({}, status=405)
    id = request.POST['id']
    doc_template = DocumentTemplate.objects.filter(
        Q(id=id),
        Q(user=request.user) | Q(user=None)
    ).first()
    if doc_template is None:
        return JsonResponse({}, status=405)
    response = {}
    status = 201
    citation_styles = list(doc_template.citation_styles.all())
    document_styles = list(doc_template.documentstyle_set.all())
    export_templates = list(doc_template.exporttemplate_set.all())
    doc_template.pk = None
    doc_template.user = request.user
    doc_template.save()
    for cs in citation_styles:
        doc_template.citation_styles.add(cs)
    for ds in document_styles:
        style_files = list(ds.documentstylefile_set.all())
        ds.pk = None
        ds.document_template = doc_template
        ds.save()
        for sf in style_files:
            sf.pk = None
            sf.style = ds
            sf.save()
    for et in export_templates:
        et.pk = None
        et.document_template = doc_template
        et.save()
    response['new_id'] = doc_template.id
    return JsonResponse(
        response,
        status=status
    )


@login_required
def delete(request):
    response = {}
    status = 405
    if request.is_ajax() and request.method == 'POST':
        id = int(request.POST['id'])
        doc_template = DocumentTemplate.objects.filter(
            pk=id,
            user=request.user
        ).first()
        if doc_template:
            status = 200
            if doc_template.is_deletable():
                doc_template.delete()
                response['done'] = True
            else:
                response['done'] = False
    return JsonResponse(
        response,
        status=status
    )
