"""
Unit tests for OrderRepositoryImpl.
All external dependencies (SQLAlchemy Session) are mocked.
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from unittest.mock import MagicMock

from order_management.domain.models import (
    Money,
    Order,
    OrderItem,
    OrderStatus,
)
from order_management.infrastructure.adapters.output.persistence.order_repository_impl import (
    OrderRepositoryImpl,
)
from order_management.infrastructure.adapters.output.persistence.models import (
    OrderItemModel,
    OrderModel,
)


class TestOrderRepositoryImpl:
    """Test suite for OrderRepositoryImpl."""

    @pytest.fixture
    def session(self):
        """Mock SQLAlchemy Session."""
        return MagicMock()

    @pytest.fixture
    def repo(self, session):
        return OrderRepositoryImpl(session=session)

    @pytest.fixture
    def customer_id(self):
        return uuid4()

    @pytest.fixture
    def product_id(self):
        return uuid4()

    @pytest.fixture
    def domain_order(self, customer_id, product_id):
        item = OrderItem(
            product_id=product_id,
            product_name="Repo Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00")),
        )
        return Order.create(customer_id=customer_id, items=[item])

    def test_save_new_order_adds_to_session(self, repo, session, domain_order):
        # Arrange: no existing order
        session.query.return_value.filter.return_value.first.return_value = None
        # Act
        result = repo.save(domain_order)
        # Assert
        assert result is domain_order
        session.add.assert_called_once()
        call_arg = session.add.call_args[0][0]
        assert isinstance(call_arg, OrderModel)
        assert call_arg.id == str(domain_order.order_id)
        assert call_arg.customer_id == str(domain_order.customer_id)
        assert call_arg.status == OrderStatus.PENDING.value
        session.flush.assert_called()

    def test_save_existing_order_updates_and_flush(self, repo, session, domain_order):
        # Arrange: existing order in DB
        existing_model = OrderModel(
            id=str(domain_order.order_id),
            customer_id=str(domain_order.customer_id),
            status=OrderStatus.PENDING.value,
            total_amount=Decimal("20.00"),
            currency="USD",
        )
        existing_model.items = []
        session.query.return_value.filter.return_value.first.return_value = existing_model
        # Act
        result = repo.save(domain_order)
        # Assert
        assert result is domain_order
        session.add.assert_not_called()
        assert existing_model.customer_id == str(domain_order.customer_id)
        assert existing_model.status == domain_order.status.value
        session.flush.assert_called()

    def test_find_by_id_returns_none_when_not_found(self, repo, session):
        # find_by_id uses .options(joinedload(...)).filter(...).first()
        chain = session.query.return_value.options.return_value.filter.return_value
        chain.first.return_value = None
        order_id = uuid4()
        result = repo.find_by_id(order_id)
        assert result is None

    def test_find_by_id_returns_domain_order_when_found(self, repo, session):
        order_id = uuid4()
        customer_id = uuid4()
        product_id = uuid4()
        item_row = OrderItemModel(
            id=str(uuid4()),
            order_id=str(order_id),
            product_id=str(product_id),
            product_name="Found Product",
            quantity=1,
            unit_price=Decimal("15.00"),
            currency="USD",
        )
        order_row = OrderModel(
            id=str(order_id),
            customer_id=str(customer_id),
            status=OrderStatus.PAID.value,
            total_amount=Decimal("15.00"),
            currency="USD",
        )
        order_row.items = [item_row]
        # find_by_id uses .options(joinedload(...)).filter(...).first()
        session.query.return_value.options.return_value.filter.return_value.first.return_value = order_row
        result = repo.find_by_id(order_id)
        assert result is not None
        assert result.order_id == order_id
        assert result.customer_id == customer_id
        assert result.status == OrderStatus.PAID
        assert len(result.items) == 1
        assert result.items[0].product_name == "Found Product"

    def test_find_by_customer_id_returns_empty_list_when_none(self, repo, session):
        # find_by_customer_id uses .options(joinedload(...)).filter(...).all()
        session.query.return_value.options.return_value.filter.return_value.all.return_value = []
        result = repo.find_by_customer_id(uuid4())
        assert result == []

    def test_find_by_customer_id_returns_list_of_orders(self, repo, session):
        customer_id = uuid4()
        order_id = uuid4()
        product_id = uuid4()
        item_row = OrderItemModel(
            id=str(uuid4()),
            order_id=str(order_id),
            product_id=str(product_id),
            product_name="Customer Product",
            quantity=1,
            unit_price=Decimal("10.00"),
            currency="USD",
        )
        order_row = OrderModel(
            id=str(order_id),
            customer_id=str(customer_id),
            status=OrderStatus.PENDING.value,
            total_amount=Decimal("10.00"),
            currency="USD",
        )
        order_row.items = [item_row]
        # find_by_customer_id uses .options(joinedload(...)).filter(...).all()
        session.query.return_value.options.return_value.filter.return_value.all.return_value = [order_row]
        result = repo.find_by_customer_id(customer_id)
        assert len(result) == 1
        assert result[0].order_id == order_id
        assert result[0].customer_id == customer_id

    def test_delete_returns_false_when_order_not_found(self, repo, session):
        session.query.return_value.filter.return_value.first.return_value = None
        result = repo.delete(uuid4())
        assert result is False
        session.delete.assert_not_called()

    def test_delete_returns_true_and_deletes_when_found(self, repo, session):
        order_id = uuid4()
        order_row = OrderModel(
            id=str(order_id),
            customer_id=str(uuid4()),
            status=OrderStatus.PENDING.value,
            total_amount=Decimal("10.00"),
            currency="USD",
        )
        session.query.return_value.filter.return_value.first.return_value = order_row
        result = repo.delete(order_id)
        assert result is True
        session.delete.assert_called_once_with(order_row)
        session.flush.assert_called()
