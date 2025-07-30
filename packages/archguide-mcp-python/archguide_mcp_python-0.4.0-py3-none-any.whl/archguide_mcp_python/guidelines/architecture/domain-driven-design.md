---
id: architecture-domain-driven-design
title: Domain Driven Design (DDD) Architecture
category: architecture
subcategory: domain-modeling
version: 1.0.0
tags: [ddd, domain-modeling, bounded-context, aggregate, architecture, tactical-patterns, strategic-patterns]
author: Architecture Team
created: 2025-01-25
lastUpdated: 2025-01-25
applicability: [enterprise, complex-domains, large-teams, long-term-projects]
techStack: [python, java, csharp, typescript, any-oop-language]
prerequisites: [object-oriented-programming, design-patterns, software-architecture-basics]
relatedGuidelines: [microservices-patterns, event-driven-architecture, hexagonal-architecture]
---

# Domain Driven Design (DDD) Architecture

Domain Driven Design is a software development approach that focuses on modeling complex business domains through collaboration between technical and domain experts. DDD provides strategic and tactical patterns for building maintainable, scalable software systems that closely reflect business requirements.

## Core Philosophy

DDD emphasizes:
1. **Domain Focus**: The primary focus should be on the domain and domain logic
2. **Collaboration**: Close collaboration between developers and domain experts
3. **Ubiquitous Language**: A common language shared across the team
4. **Iterative Refinement**: Continuous refinement of the domain model

## Strategic Design Patterns

### Bounded Context
The fundamental pattern that defines clear boundaries within which a domain model is consistent.

### Context Mapping
Understanding and documenting relationships between different bounded contexts.

### Ubiquitous Language
A common vocabulary that is shared between developers, domain experts, and stakeholders.

## Tactical Design Patterns

## Pattern: Bounded Context

### Description
A logical boundary within which a domain model is consistent and unified. Each bounded context has its own ubiquitous language and can be developed independently.

### When to use
- When working with large, complex domains
- When different parts of the system have different business rules
- When you need to manage complexity by creating clear boundaries
- When multiple teams are working on the same system

### Implementation
Define explicit boundaries around related business concepts and ensure each context has its own ubiquitous language. Implement clear interfaces between contexts.

### Consequences
- Clear separation of concerns
- Reduced coupling between domains
- Independent development and deployment
- May require integration patterns between contexts
- Need for context mapping and coordination

### Example: E-commerce Bounded Contexts
```python
# Order Management Context
class Order:
    """Order aggregate in Order Management context"""
    def __init__(self, order_id: str, customer_id: str):
        self.id = order_id
        self.customer_id = customer_id
        self.status = OrderStatus.PENDING
        self.lines = []
    
    def add_line(self, product_id: str, quantity: int, price: Money):
        """Business rule: Can only add lines to pending orders"""
        if self.status != OrderStatus.PENDING:
            raise OrderModificationError("Cannot modify confirmed order")
        
        self.lines.append(OrderLine(product_id, quantity, price))

# Inventory Management Context (separate bounded context)
class Product:
    """Product aggregate in Inventory context"""
    def __init__(self, product_id: str, name: str, stock_level: int):
        self.id = product_id
        self.name = name
        self.stock_level = stock_level
    
    def reserve_stock(self, quantity: int):
        """Business rule: Cannot reserve more than available stock"""
        if quantity > self.stock_level:
            raise InsufficientStockError(f"Only {self.stock_level} items available")
        
        self.stock_level -= quantity

# Integration between contexts via domain events
class OrderConfirmedEvent:
    def __init__(self, order_id: str, order_lines: List[Dict]):
        self.order_id = order_id
        self.order_lines = order_lines
        self.occurred_at = datetime.utcnow()
```

## Pattern: Aggregate Root

### Description
A cluster of domain objects that can be treated as a single unit for data changes. The aggregate root is the only entry point for modifying the aggregate's internal state.

### When to use
- When you need to maintain business invariants across related entities
- When you need clear transaction boundaries
- When you want to ensure consistency within a group of objects

### Implementation
Design aggregates with a single root entity that controls access to all internal entities. Keep aggregates small and focused on a single business concept.

### Consequences
- Strong consistency within aggregate boundaries
- Clear transaction boundaries
- Simplified persistence and loading
- Potential performance constraints with large aggregates
- Need careful design to avoid overly large aggregates

### Example: Order Aggregate
```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from decimal import Decimal

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass(frozen=True)
class Money:
    """Value object for monetary amounts"""
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

@dataclass
class OrderLine:
    """Entity within Order aggregate"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: Money
    
    def total_price(self) -> Money:
        return Money(
            amount=self.unit_price.amount * self.quantity,
            currency=self.unit_price.currency
        )

class Order:
    """Aggregate Root for Order domain"""
    
    def __init__(self, order_id: str, customer_id: str):
        self._id = order_id
        self._customer_id = customer_id
        self._status = OrderStatus.PENDING
        self._order_lines: List[OrderLine] = []
        self._created_at = datetime.utcnow()
    
    def add_order_line(self, product_id: str, product_name: str, 
                      quantity: int, unit_price: Money):
        """Business rule: Can only add lines to pending orders"""
        if self._status != OrderStatus.PENDING:
            raise OrderModificationError("Cannot modify confirmed order")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check if product already exists in order
        existing_line = next(
            (line for line in self._order_lines if line.product_id == product_id), 
            None
        )
        
        if existing_line:
            existing_line.quantity += quantity
        else:
            line = OrderLine(product_id, product_name, quantity, unit_price)
            self._order_lines.append(line)
    
    def confirm_order(self):
        """Business rule: Order must have at least one line to confirm"""
        if not self._order_lines:
            raise OrderValidationError("Cannot confirm empty order")
        
        if self.total_amount().amount < Money(Decimal('0.01'), 'USD').amount:
            raise OrderValidationError("Order total must be positive")
        
        self._status = OrderStatus.CONFIRMED
    
    def total_amount(self) -> Money:
        if not self._order_lines:
            return Money(Decimal('0'), 'USD')
        
        total = sum(line.total_price().amount for line in self._order_lines)
        currency = self._order_lines[0].unit_price.currency
        return Money(total, currency)
    
    # Properties to expose internal state (read-only)
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def order_lines(self) -> List[OrderLine]:
        return self._order_lines.copy()  # Return copy to prevent external modification
```

## Pattern: Domain Service

### Description
A service that encapsulates domain logic that doesn't naturally fit within an entity or value object, typically operations that involve multiple aggregates.

### When to use
- When business logic spans multiple entities or aggregates
- When the logic doesn't belong to a specific entity
- When you need to coordinate between different domain objects
- When implementing complex business rules or calculations

### Implementation
Create stateless services that operate on domain objects and implement business rules. Keep them focused on domain concerns, not technical concerns.

### Consequences
- Cleaner entity design by avoiding inappropriate responsibilities
- Reusable business logic across different contexts
- Risk of creating anemic domain model if overused
- Clear separation of cross-aggregate business logic

### Example: Pricing Domain Service
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class PricingService:
    """Domain Service for complex pricing calculations"""
    
    def __init__(self, discount_policy: "DiscountPolicy", 
                 tax_calculator: "TaxCalculator"):
        self._discount_policy = discount_policy
        self._tax_calculator = tax_calculator
    
    def calculate_order_total(self, order: Order, customer: Customer) -> Money:
        """
        Complex pricing logic that spans multiple aggregates
        """
        # Base calculation from order lines
        subtotal = order.total_amount()
        
        # Apply customer-specific discounts (business rule involving multiple aggregates)
        discount = self._discount_policy.calculate_discount(order, customer)
        discounted_amount = Money(
            amount=subtotal.amount - discount.amount,
            currency=subtotal.currency
        )
        
        # Calculate taxes based on customer location and products
        tax = self._tax_calculator.calculate_tax(order, customer.address)
        
        final_total = Money(
            amount=discounted_amount.amount + tax.amount,
            currency=subtotal.currency
        )
        
        return final_total
    
    def apply_bulk_discount(self, orders: List[Order], customer: Customer) -> Dict[str, Money]:
        """Business logic for bulk order discounts"""
        total_value = sum(order.total_amount().amount for order in orders)
        
        # Business rule: 5% discount for orders over $10,000
        if total_value > Decimal('10000'):
            discount_rate = Decimal('0.05')
            return {
                order.id: Money(
                    amount=order.total_amount().amount * discount_rate,
                    currency=order.total_amount().currency
                )
                for order in orders
            }
        
        return {}
```

## Pattern: Repository

### Description
Provides an abstraction for accessing aggregates, encapsulating the logic needed to access data sources.

### When to use
- When you need to persist and retrieve aggregates
- When you want to decouple domain model from persistence concerns
- When you need to support multiple storage mechanisms
- When implementing testing with mock repositories

### Implementation
Define repository interfaces in the domain layer and implement them in the infrastructure layer. Focus on aggregate roots only.

### Consequences
- Clean separation between domain and persistence
- Testable domain logic with mock repositories
- Flexibility to change storage mechanisms
- Additional abstraction layer complexity

### Example: Order Repository
```python
from abc import ABC, abstractmethod
from typing import Optional, List

class OrderRepository(ABC):
    """Repository interface for Order aggregate"""
    
    @abstractmethod
    async def save(self, order: Order) -> None:
        """Save an order aggregate"""
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional[Order]:
        """Find order by ID"""
        pass
    
    @abstractmethod
    async def find_by_customer(self, customer_id: str) -> List[Order]:
        """Find all orders for a customer"""
        pass

class SqlOrderRepository(OrderRepository):
    """SQL implementation of OrderRepository"""
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
    
    async def save(self, order: Order) -> None:
        async with self._session_factory() as session:
            # Map domain object to database entities
            order_entity = self._to_entity(order)
            session.merge(order_entity)  # Use merge for updates
            await session.commit()
    
    async def find_by_id(self, order_id: str) -> Optional[Order]:
        async with self._session_factory() as session:
            order_entity = await session.get(OrderEntity, order_id)
            return self._to_domain_object(order_entity) if order_entity else None
    
    def _to_entity(self, order: Order) -> "OrderEntity":
        """Convert domain object to database entity"""
        return OrderEntity(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            created_at=order.created_at
        )
    
    def _to_domain_object(self, entity: "OrderEntity") -> Order:
        """Reconstruct domain object from database entity"""
        order = Order(entity.id, entity.customer_id)
        # Restore status and other properties
        order._status = OrderStatus(entity.status)
        return order
```

## Anti-pattern: Anemic Domain Model

### Description
Domain objects with little or no business logic, essentially just data containers with getters and setters.

### Why it's bad
- Violates DDD principles by separating data from behavior
- Leads to procedural programming instead of object-oriented design
- Business logic scattered across service classes
- Difficult to maintain and understand business rules
- Poor encapsulation of domain concepts

### Instead
Put behavior in domain objects where it belongs, creating rich domain models that encapsulate both data and business logic.

## Anti-pattern: God Aggregate

### Description
An aggregate that tries to manage too many entities and business rules, becoming overly complex and difficult to maintain.

### Why it's bad
- Leads to performance issues due to large object graphs
- Creates complex transactions that are hard to manage
- Reduces scalability and increases contention
- Violates single responsibility principle
- Makes testing and maintenance difficult

### Instead
Split large aggregates into smaller, focused aggregates with clear boundaries. Use domain events for coordination between aggregates.

## Best Practices

1. **Start with Strategic Design**
   - Identify bounded contexts through domain exploration
   - Establish ubiquitous language for each context
   - Map relationships between contexts
   - Focus on the most complex/valuable areas first

2. **Keep Aggregates Small**
   - Design aggregates around single business concepts
   - Prefer composition over large inheritance hierarchies
   - Use eventual consistency between aggregates
   - Reference other aggregates by ID only

3. **Implement Rich Domain Models**
   - Put business logic in domain objects
   - Use value objects for concepts without identity
   - Encapsulate business rules within aggregates
   - Avoid anemic domain models

4. **Use Domain Events for Integration**
   - Coordinate between aggregates using domain events
   - Implement eventual consistency through events
   - Decouple bounded contexts with events
   - Consider event sourcing for complex domains

5. **Maintain Domain Focus**
   - Keep business logic in the domain layer
   - Avoid leaking domain concepts to infrastructure
   - Use repositories for persistence abstraction
   - Regular refine the model based on new insights

## When NOT to Use DDD

DDD may not be appropriate when:
- Working with simple CRUD applications
- Domain complexity is low
- Short-term projects with limited scope
- Small teams with limited resources
- Technical requirements dominate business requirements