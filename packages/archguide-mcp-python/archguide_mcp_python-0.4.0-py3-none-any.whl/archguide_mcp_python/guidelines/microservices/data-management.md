---
id: microservices-data-management
title: Data Management in Microservices Architecture
category: microservices
subcategory: data-patterns
version: 2.0.0
tags: [microservices, data, distributed-systems, database-per-service, event-sourcing, saga-pattern]
author: Architecture Team
created: 2024-01-15
lastUpdated: 2025-01-15
applicability: [enterprise, cloud-native, scalable-systems]
techStack: [python, fastapi, kafka, postgresql, mongodb]
prerequisites: [microservices-basics, distributed-systems-fundamentals]
relatedGuidelines: [event-driven-architecture, api-design-guidelines]
---

# Data Management in Microservices Architecture

Managing data in a microservices architecture requires careful consideration of data ownership, consistency, and communication patterns. This guideline provides patterns and best practices for effective data management.

## Core Principles

1. **Service Autonomy**: Each service should be able to function independently
2. **Data Ownership**: Each service owns its data and exposes it through APIs
3. **Eventual Consistency**: Accept eventual consistency for better scalability
4. **No Shared Databases**: Avoid direct database sharing between services

## Pattern: Database per Service

### Description
Each microservice owns its database schema and data. No other service can access this data directly.

### When to use
- When services need to be independently deployable
- When teams need autonomy over their data models
- When services have different data storage requirements

### Implementation
Services expose their data through well-defined APIs rather than allowing direct database access.

### Consequences
- Service independence and loose coupling
- Technology diversity (different databases for different services)
- Increased complexity in cross-service data queries
- Need for distributed transaction management

### Example: Order Service Implementation
This example shows how an Order Service manages its own database:

```python
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

@app.post("/api/orders", response_model=OrderResponse)
async def create_order(request: OrderRequest, db: Session = Depends(get_db)):
    """Create a new order - service owns the order data."""
    order = Order(**request.dict())
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Publish event for other services
    await event_publisher.publish(OrderCreatedEvent(order))
    
    return OrderResponse.from_orm(order)

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get order by ID - data exposed through API, not direct DB access."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderResponse.from_orm(order)
```

## Pattern: Event Sourcing

### Description
Store all changes to application state as a sequence of events. The current state is derived by replaying these events.

### When to use
- When you need a complete audit trail
- When you need to support temporal queries
- When implementing CQRS pattern

### Implementation
Instead of storing current state, store all events that led to that state.

### Consequences
- Complete audit trail of all changes
- Ability to replay events to any point in time
- Increased storage requirements
- Complex event versioning over time

### Example: Event Store Implementation
```python
from sqlalchemy import Column, String, DateTime, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from typing import List
import json

Base = declarative_base()

class EventStore(Base):
    __tablename__ = "event_store"
    
    event_id = Column(String, primary_key=True)
    aggregate_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_data = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    version = Column(BigInteger, nullable=False)

class EventSourcingHandler:
    def __init__(self, session: Session):
        self.session = session
    
    def save_event(self, event: DomainEvent) -> None:
        """Save a domain event to the event store."""
        event_store = EventStore(
            event_id=str(uuid4()),
            aggregate_id=event.aggregate_id,
            event_type=event.__class__.__name__,
            event_data=json.dumps(event.dict()),
            timestamp=datetime.now(timezone.utc)
        )
        
        self.session.add(event_store)
        self.session.commit()
    
    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        """Get all events for an aggregate."""
        events = self.session.query(EventStore)\
            .filter(EventStore.aggregate_id == aggregate_id)\
            .order_by(EventStore.timestamp)\
            .all()
        
        return [self._deserialize(event) for event in events]
    
    def _deserialize(self, event_store: EventStore) -> DomainEvent:
        """Deserialize event from storage."""
        event_data = json.loads(event_store.event_data)
        event_class = globals()[event_store.event_type]  # In real code, use proper registry
        return event_class(**event_data)
```

## Anti-pattern: Shared Database

### Description
Multiple microservices directly access the same database schema.

### Why it's bad
- Creates tight coupling between services
- Makes independent deployment impossible
- Schema changes affect multiple services
- Violates service autonomy principle

### Instead
Use API calls or events to share data between services. Each service should have its own database.

## Anti-pattern: Distributed Transactions

### Description
Using two-phase commit or XA transactions across multiple microservices.

### Why it's bad
- Poor performance and scalability
- Increases coupling between services
- Complex failure handling
- Blocks resources during transaction

### Instead
Use the Saga pattern with compensating transactions for distributed workflows.

## Best Practices

1. **Design for Eventual Consistency**
   - Use asynchronous communication where possible
   - Implement idempotent operations
   - Handle duplicate events gracefully

2. **Implement Data Privacy**
   - Don't expose internal IDs in APIs
   - Use DTOs to control data exposure
   - Implement field-level access control

3. **Handle Data Synchronization**
   - Use event-driven updates
   - Implement CDC (Change Data Capture) for legacy systems
   - Consider CQRS for read-heavy workloads

4. **Monitor Data Consistency**
   - Implement health checks for data consistency
   - Use distributed tracing for data flows
   - Set up alerts for consistency violations