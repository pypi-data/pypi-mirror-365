# modal-hj3415

모달창을 띄우는 모듈.


1. 프로젝트의 settings.py 에 추가한다.
```python
INSTALLED_APPS = [
    'modal_hj3415',
]
```

2. makemigration, migrate 실행

3. 사용 위치의 html에 작성한다.
```html
{% load modal_tags %}
...
{% show_modal %}
```