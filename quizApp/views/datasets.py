"""Views for CRUD datasets.
"""
import os

from werkzeug.datastructures import CombinedMultiDict
from flask import Blueprint, render_template, url_for, abort, \
    request
from flask_security import roles_required

from quizApp.forms.common import DeleteObjectForm, ObjectTypeForm
from quizApp.forms.datasets import DatasetForm, GraphForm, TextForm
from quizApp.models import Dataset, MediaItem
from quizApp.views.helpers import validate_model_id
from quizApp.views.common import ObjectCollectionView, ObjectView

datasets = Blueprint("datasets", __name__, url_prefix="/datasets")

MEDIA_ITEM_TYPES = {
    "graph": "Graph",
    "text": "Text",
}
DATASET_ROUTE = "/<int:dataset_id>"
MEDIA_ITEMS_ROUTE = os.path.join(DATASET_ROUTE + "/media_items/")
MEDIA_ITEM_ROUTE = os.path.join(MEDIA_ITEMS_ROUTE + "<int:media_item_id>")


class DatasetCollectionView(ObjectCollectionView):
    """View for managing a collection of Datasets.
    """
    decorators = [roles_required("experimenter")]
    methods = ["GET", "POST"]
    resolve_kwargs = dict
    template = "datasets/read_datasets.html"

    def create_form(self):
        return DatasetForm(request.form)

    def get_members(self):
        return Dataset.query.all()

    def create_member(self, create_form):
        dataset = Dataset()
        create_form.populate_obj(dataset)
        dataset.save()
        return {"next_url": url_for("datasets.settings_dataset",
                                    dataset_id=dataset.id)}

datasets.add_url_rule("/",
                      view_func=DatasetCollectionView.as_view('datasets'))


class DatasetView(ObjectView):
    """View for handling a particular dataset.
    """
    methods = ["PUT", "DELETE"]
    object_key = "dataset"

    def resolve_kwargs(self, dataset_id):
        return {"dataset": validate_model_id(Dataset, dataset_id)}

    def update_form(self, **_):
        return DatasetForm(request.form)

    def collection_url(self, **kwargs):
        return url_for("datasets.datasets")

datasets.add_url_rule(DATASET_ROUTE,
                      view_func=DatasetView.as_view('dataset'))


class MediaItemView(ObjectView):
    """View for handling a particular media item
    """
    methods = ["DELETE", "PUT", "GET"]
    object_key = "media_item"
    template = "datasets/read_media_item.html"

    def update_form(self, media_item, **_):
        update_form_mapping = {
            "graph": GraphForm(CombinedMultiDict((request.form,
                                                  request.files))),
            "text": TextForm(request.form),
        }
        return update_form_mapping[media_item.type]

    def collection_url(self, dataset, **_):
        return url_for("datasets.settings_dataset", dataset_id=dataset.id)

    def resolve_kwargs(self, dataset_id, media_item_id):
        dataset = validate_model_id(Dataset, dataset_id)
        media_item = validate_model_id(MediaItem, media_item_id)

        if media_item.dataset != dataset:
            abort(404)

        return {"dataset": dataset, "media_item": media_item}


datasets.add_url_rule(MEDIA_ITEM_ROUTE,
                      view_func=MediaItemView.as_view('media_item'))


@datasets.route(DATASET_ROUTE + '/settings', methods=["GET"])
@roles_required("experimenter")
def settings_dataset(dataset_id):
    """View the configuration of a particular dataset.
    """
    dataset = validate_model_id(Dataset, dataset_id)

    update_dataset_form = DatasetForm(obj=dataset)

    create_media_item_form = ObjectTypeForm()
    create_media_item_form.populate_object_type(MEDIA_ITEM_TYPES)
    confirm_delete_media_item_form = DeleteObjectForm()

    return render_template(
        "datasets/settings_dataset.html",
        dataset=dataset,
        update_dataset_form=update_dataset_form,
        confirm_delete_media_item_form=confirm_delete_media_item_form,
        create_media_item_form=create_media_item_form)


class MediaItemCollectionView(ObjectCollectionView):
    """Manage a collection of MediaItems.
    """
    decorators = [roles_required("experimenter")]
    methods = ["POST"]
    get_members = None
    template = None

    def resolve_kwargs(self, dataset_id):
        dataset = validate_model_id(Dataset, dataset_id)
        return {"dataset": dataset}

    def create_form(self):
        create_media_item_form = ObjectTypeForm()
        create_media_item_form.populate_object_type(MEDIA_ITEM_TYPES)
        return create_media_item_form

    def create_member(self, create_form, dataset):
        media_item = MediaItem(type=create_form.object_type.data,
                               dataset=dataset)
        media_item.save()

        return {
            "next_url": url_for("datasets.settings_media_item",
                                dataset_id=dataset.id,
                                media_item_id=media_item.id),
        }

datasets.add_url_rule(MEDIA_ITEMS_ROUTE,
                      view_func=MediaItemCollectionView.as_view('media_items'))


@datasets.route(MEDIA_ITEM_ROUTE + "/settings", methods=["GET"])
@roles_required("experimenter")
def settings_media_item(dataset_id, media_item_id):
    """View the configuration of some media item.

    Ultimately this view dispatches to another view for the specific type
    of media item.
    """
    dataset = validate_model_id(Dataset, dataset_id)
    media_item = validate_model_id(MediaItem, media_item_id)
    create_media_item_form = ObjectTypeForm()
    create_media_item_form.populate_object_type(MEDIA_ITEM_TYPES)

    if media_item not in dataset.media_items:
        abort(404)

    template = "datasets/settings_media_item.html"

    update_form_class_mapping = {
        "graph": GraphForm,
        "text": TextForm,
    }

    update_form_cls = update_form_class_mapping[media_item.type]

    return render_template(
        template,
        update_media_item_form=update_form_cls(obj=media_item),
        dataset=dataset,
        create_media_item_form=create_media_item_form,
        media_item=media_item)
