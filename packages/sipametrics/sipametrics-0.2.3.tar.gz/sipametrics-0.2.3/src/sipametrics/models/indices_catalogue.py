import typing
import sipametrics.models.base as base_models
import sipametrics.constants as CONSTANTS


class IndicesCatalogueRequest(base_models.CamelCaseBaseModel):
    product: CONSTANTS.Product
    app: typing.Optional[CONSTANTS.App] = None

    def to_dict(self) -> dict:
        payload:dict[str, typing.Union[str, int]] = { "product": self.product.value if isinstance(self.product, CONSTANTS.Product) else self.product }
        if self.app:
            if self.app == CONSTANTS.App.MARKET_INDICES:
                app_key = "marketIndices" if self.product == CONSTANTS.Product.PRIVATE_EQUITY else "indexApp"
                payload[app_key] = 1
            elif self.app == CONSTANTS.App.THEMATIC_INDICES:
                app_key = "peccsBenchmarks" if self.product == CONSTANTS.Product.PRIVATE_EQUITY else "assetValuation"
                payload[app_key] = 1

        return payload