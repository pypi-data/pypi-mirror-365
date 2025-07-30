from typing import List

import strawberry
import strawberry_django

from .types import (
    InventoryMonitorABRAType,
    InventoryMonitorAssetType,
    InventoryMonitorAssetTypeType,
    InventoryMonitorAssetServiceType,
    InventoryMonitorContractType,
    InventoryMonitorContractorType,
    InventoryMonitorInvoiceType,
    InventoryMonitorProbeType,
    InventoryMonitorRMAType,
)


@strawberry.type(name="Query")
class InventoryMonitorABRAQuery:
    inventory_monitor_abra: InventoryMonitorABRAType = strawberry_django.field()
    inventory_monitor_abra_list: List[InventoryMonitorABRAType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorAssetQuery:
    inventory_monitor_asset: InventoryMonitorAssetType = strawberry_django.field()
    inventory_monitor_asset_list: List[InventoryMonitorAssetType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorAssetTypeQuery:
    inventory_monitor_asset_type: InventoryMonitorAssetTypeType = strawberry_django.field()
    inventory_monitor_asset_type_list: List[InventoryMonitorAssetTypeType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorAssetServiceQuery:
    inventory_monitor_asset_service: InventoryMonitorAssetServiceType = strawberry_django.field()
    inventory_monitor_asset_service_list: List[InventoryMonitorAssetServiceType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorContractQuery:
    inventory_monitor_contract: InventoryMonitorContractType = strawberry_django.field()
    inventory_monitor_contract_list: List[InventoryMonitorContractType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorContractorQuery:
    inventory_monitor_contractor: InventoryMonitorContractorType = strawberry_django.field()
    inventory_monitor_contractor_list: List[InventoryMonitorContractorType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorInvoiceQuery:
    inventory_monitor_invoice: InventoryMonitorInvoiceType = strawberry_django.field()
    inventory_monitor_invoice_list: List[InventoryMonitorInvoiceType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorProbeQuery:
    inventory_monitor_probe: InventoryMonitorProbeType = strawberry_django.field()
    inventory_monitor_probe_list: List[InventoryMonitorProbeType] = strawberry_django.field()


@strawberry.type(name="Query")
class InventoryMonitorRMAQuery:
    inventory_monitor_rma: InventoryMonitorRMAType = strawberry_django.field()
    inventory_monitor_rma_list: List[InventoryMonitorRMAType] = strawberry_django.field()
