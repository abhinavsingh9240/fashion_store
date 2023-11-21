from home.models import Section, Size


def categories(request):
    section_men = Section.objects.filter(id=1).first()
    categories_men = section_men.category_set.all().order_by("-id")
    section_women = Section.objects.filter(id=2).first()
    categories_women = section_women.category_set.all().order_by("-id")
    context = {
        "categories_men": categories_men,
        "categories_women": categories_women
    }
    return context


def sizes_n_sections(request):
    sizes = Size.objects.all()
    sections = Section.objects.all()
    context = {
        "sizes": sizes,
        "sections" : sections,
    }
    return context
