from http import HTTPStatus
from typing import List

from kentik_api.api_calls import saved_filters
from kentik_api.api_connection.api_connector_protocol import APIConnectorProtocol
from kentik_api.public.saved_filter import SavedFilter
from kentik_api.requests_payload import saved_filters_payload
from kentik_api.requests_payload.as_dict import as_dict


class SavedFiltersAPI:
    """Exposes Kentik API operations related to saved filters. """

    def __init__(self, api_connector: APIConnectorProtocol) -> None:
        self._api_connector = api_connector

    def get_all(self) -> List[SavedFilter]:
        api_call = saved_filters.get_saved_filters()
        response = self._api_connector.send(api_call)
        return saved_filters_payload.GetAllResponse.from_json(response.text).to_saved_filters()

    def get(self, saved_filter_id: int) -> SavedFilter:
        api_call = saved_filters.get_saved_filter_info(saved_filter_id)
        response = self._api_connector.send(api_call)
        return saved_filters_payload.GetResponse.from_json(response.text).to_saved_filter()

    def create(self, saved_filter: SavedFilter) -> SavedFilter:
        SavedFiltersAPI.check_fields(saved_filter)

        api_call = saved_filters.create_saved_filter()
        payload = as_dict(saved_filters_payload.CreateRequest(saved_filter))
        response = self._api_connector.send(api_call, payload)
        return saved_filters_payload.CreateResponse.from_json(response.text).to_saved_filter()

    def update(self, saved_filter: SavedFilter) -> SavedFilter:
        assert saved_filter.id is not None, "SavedFilter ID has to be provided"
        SavedFiltersAPI.check_fields(saved_filter)

        api_call = saved_filters.update_saved_filter(saved_filter.id)
        payload = as_dict(saved_filters_payload.UpdateRequest(saved_filter))
        response = self._api_connector.send(api_call, payload)
        return saved_filters_payload.UpdateResponse.from_json(response.text).to_saved_filter()

    def delete(self, saved_filter_id: int) -> bool:
        api_call = saved_filters.delete_saved_filter(saved_filter_id)
        response = self._api_connector.send(api_call)
        return response.http_status_code == HTTPStatus.NO_CONTENT

    @staticmethod
    def check_fields(saved_filter: SavedFilter):
        assert saved_filter.filter_name is not None, "Filter must have name"
        if saved_filter.filters is not None:
            assert saved_filter.filters.connector is not None
            assert all(i.connector is not None for i in saved_filter.filters.filterGroups)
            assert all(i.not_ is not None for i in saved_filter.filters.filterGroups)
