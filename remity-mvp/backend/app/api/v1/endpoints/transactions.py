from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid
from typing import List
from decimal import Decimal, ROUND_HALF_UP

from app import crud, models, schemas # Import from top-level __init__ files
from app.api import dependencies # Import dependencies
from app.core.config import settings
# Placeholder for external service integrations
# from app.services import exchange_rate_service, payment_service

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Placeholder Functions (Replace with actual service calls) ---

async def get_live_exchange_rate(source_currency: str, target_currency: str) -> Decimal:
    """ Placeholder: Get exchange rate from Binance/provider. """
    # TODO: Implement actual call to Binance API or other provider
    # Handle potential errors from the API call
    logger.warning(f"Using placeholder exchange rate for {source_currency}->{target_currency}")
    # Example fixed rates for MVP simulation
    rates = {
        ("USD", "MXN"): Decimal("19.85"),
        ("MXN", "USD"): Decimal("1.0") / Decimal("19.85"),
        ("USD", "USDC"): Decimal("1.0"), # Assuming 1:1 for stablecoin
        ("USDC", "USD"): Decimal("1.0"),
        ("USDC", "MXN"): Decimal("19.80"), # Slight difference simulating crypto leg
         # Add other pairs as needed (EUR->PHP etc.)
    }
    rate = rates.get((source_currency, target_currency))
    if rate is None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"Exchange rate for {source_currency}->{target_currency} not available.")
    return rate

def calculate_fees(source_currency: str, source_amount: Decimal) -> tuple[Decimal, Decimal]:
    """ Placeholder: Calculate Remity fee and estimated payment provider fee. """
    # TODO: Implement actual fee logic (e.g., percentage, fixed, tiered)
    # TODO: Get estimated Stripe fee based on card type/region if possible
    logger.warning("Using placeholder fee calculation")
    remity_fee_percentage = Decimal("0.01") # Example: 1% Remity fee
    remity_fee = (source_amount * remity_fee_percentage).quantize(Decimal("0.01"), ROUND_HALF_UP)
    # Example fixed Stripe fee estimate
    payment_provider_fee = Decimal("0.30") + (source_amount * Decimal("0.029")).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return remity_fee, payment_provider_fee

async def create_stripe_payment_intent(amount: int, currency: str, transaction_id: uuid.UUID) -> tuple[str, str]:
    """ Placeholder: Create a Payment Intent with Stripe. """
    # TODO: Implement actual Stripe API call
    # amount should be in the smallest currency unit (e.g., cents for USD)
    # currency should be lowercase (e.g., 'usd')
    # Add metadata like transaction_id
    logger.warning(f"Using placeholder Stripe Payment Intent creation for transaction {transaction_id}")
    # Simulate response
    payment_intent_id = f"pi_{uuid.uuid4().hex[:24]}" # Fake PI ID
    client_secret = f"{payment_intent_id}_secret_{uuid.uuid4().hex}" # Fake client secret
    return payment_intent_id, client_secret

# --- End Placeholder Functions ---


@router.post("/quote", response_model=schemas.TransactionQuoteResponse)
async def get_transaction_quote(
    *,
    quote_request: schemas.TransactionQuoteRequest,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_verified_user), # Requires verified user
) -> schemas.TransactionQuoteResponse:
    """
    Get a quote for a potential transaction, including exchange rate and fees.
    Requires KYC-verified user.
    """
    logger.info(f"User {current_user.email} requesting quote: {quote_request.source_currency} -> {quote_request.target_currency}")

    try:
        # 1. Get Base Exchange Rate (Fiat Source -> Fiat Target)
        # In a real scenario, this might involve Fiat->Crypto->Fiat rates
        # For MVP, we can simulate a direct Fiat->Fiat rate or a simple Fiat->USDC->Fiat rate
        # Example: Simulating Fiat -> Fiat directly for simplicity
        rate = await get_live_exchange_rate(quote_request.source_currency, quote_request.target_currency)

        # 2. Calculate amounts based on input
        if quote_request.source_amount is not None:
            source_amount = quote_request.source_amount.quantize(Decimal("0.00000001"), ROUND_HALF_UP) # Use 8 decimal places
            target_amount = (source_amount * rate).quantize(Decimal("0.00000001"), ROUND_HALF_UP)
        elif quote_request.target_amount is not None:
            target_amount = quote_request.target_amount.quantize(Decimal("0.00000001"), ROUND_HALF_UP)
            # Calculate source amount based on target and rate (handle division by zero if rate is 0)
            if rate == 0:
                 raise HTTPException(status_code=500, detail="Invalid exchange rate (zero).")
            source_amount = (target_amount / rate).quantize(Decimal("0.00000001"), ROUND_HALF_UP)
        else:
            # Should be caught by Pydantic validation, but double-check
            raise HTTPException(status_code=422, detail="Either source_amount or target_amount is required.")

        # 3. Calculate Fees based on the source amount
        remity_fee, payment_provider_fee = calculate_fees(quote_request.source_currency, source_amount)

        # 4. Calculate Total Cost
        total_cost = source_amount + remity_fee + payment_provider_fee

        # 5. Estimate Delivery Time (Placeholder)
        # TODO: Implement logic based on currencies, payout method, time of day etc.
        estimated_delivery_time = "1-2 business days" # Placeholder

        # 6. Prepare Response
        quote_response = schemas.TransactionQuoteResponse(
            source_currency=quote_request.source_currency,
            target_currency=quote_request.target_currency,
            source_amount=source_amount,
            target_amount=target_amount,
            exchange_rate=rate,
            remity_fee=remity_fee,
            payment_provider_fee=payment_provider_fee,
            total_cost=total_cost.quantize(Decimal("0.01"), ROUND_HALF_UP), # Show final cost in standard precision
            estimated_delivery_time=estimated_delivery_time,
            # Optional: Add quote_id (e.g., cache key) and expires_at
        )
        logger.info(f"Quote generated for user {current_user.email}: {quote_response.source_amount} {quote_response.source_currency} -> {quote_response.target_amount} {quote_response.target_currency}")

        # Optional: Cache the quote response with a short TTL (e.g., 60 seconds) using Redis

        return quote_response

    except HTTPException as http_exc:
        raise http_exc # Re-raise HTTP exceptions directly
    except Exception as e:
        logger.error(f"Error generating quote for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the quote.",
        )


@router.post("/", response_model=schemas.TransactionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    transaction_in: schemas.TransactionCreate,
    current_user: models.User = Depends(dependencies.get_current_verified_user), # Requires verified user
) -> schemas.TransactionCreateResponse:
    """
    Create a new transaction based on a quote and initiate payment.
    Requires KYC-verified user.
    """
    logger.info(f"User {current_user.email} attempting to create transaction for recipient {transaction_in.recipient_id}")

    # 1. Validate Recipient
    recipient = await crud.recipient.get_by_owner(
        db=db, recipient_id=transaction_in.recipient_id, user_id=current_user.id
    )
    if not recipient:
        logger.warning(f"Transaction creation failed: Recipient {transaction_in.recipient_id} not found or not owned by user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipient with ID {transaction_in.recipient_id} not found.",
        )
    # Add check: recipient.country_code must match transaction_in.target_currency country if applicable

    # 2. Validate Quote (Optional but recommended)
    # If using quote_id, retrieve cached/stored quote and verify details match transaction_in
    # Verify quote hasn't expired

    # 3. Create Transaction Record in DB
    try:
        db_transaction = await crud.transaction.create_with_owner_and_recipient(
            db=db, obj_in=transaction_in, user_id=current_user.id
        )
    except Exception as e:
        # CRUD logs error and rolls back
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save transaction details.",
        )

    # 4. Create Payment Intent with Stripe
    try:
        # Amount must be in the smallest currency unit (e.g., cents)
        total_cost_for_payment = transaction_in.source_amount + transaction_in.remity_fee + transaction_in.payment_provider_fee
        amount_in_cents = int(total_cost_for_payment * 100) # Assumes 2 decimal places for source currency like USD/EUR
        currency_code_lower = transaction_in.source_currency.lower()

        payment_intent_id, client_secret = await create_stripe_payment_intent(
            amount=amount_in_cents,
            currency=currency_code_lower,
            transaction_id=db_transaction.id # Pass our transaction ID as metadata
        )

        # 5. Update Transaction with Payment Intent ID
        await crud.transaction.update(
            db=db, db_obj=db_transaction, obj_in={"onramp_payment_intent_id": payment_intent_id}
        )
        logger.info(f"Stripe Payment Intent {payment_intent_id} created for transaction {db_transaction.id}")

    except Exception as e:
        logger.error(f"Failed to create Stripe Payment Intent or update transaction {db_transaction.id}: {e}", exc_info=True)
        # Attempt to mark transaction as failed? Or rely on reconciliation?
        # For now, raise error - frontend won't get client_secret
        await crud.transaction.update_status(
             db=db, transaction_id=db_transaction.id, status=TransactionStatus.FAILED, details={"failure_reason": "Payment provider interaction failed"}
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, # Indicate issue with upstream service (Stripe)
            detail="Failed to initiate payment with payment provider.",
        )

    # 6. Return response to Frontend
    # The status here might still be the initial one (e.g., quote_created)
    # It will be updated to PENDING_APPROVAL by the Stripe webhook handler upon successful payment.
    return schemas.TransactionCreateResponse(
        transaction_id=db_transaction.id,
        status=db_transaction.status, # Return current status
        onramp_payment_intent_client_secret=client_secret,
    )


@router.get("/", response_model=List[schemas.Transaction])
async def read_transactions(
    db: AsyncSession = Depends(dependencies.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(dependencies.get_current_active_user), # Any active user can view their history
) -> List[models.Transaction]:
    """
    Retrieve transaction history for the current logged-in user.
    """
    logger.info(f"User {current_user.email} fetching transactions (skip={skip}, limit={limit})")
    transactions = await crud.transaction.get_multi_by_owner(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return transactions


@router.get("/{transaction_id}", response_model=schemas.Transaction)
async def read_transaction(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> models.Transaction:
    """
    Get details of a specific transaction by ID, ensuring it belongs to the current user.
    """
    logger.info(f"User {current_user.email} fetching transaction ID: {transaction_id}")
    transaction = await crud.transaction.get_by_owner(
        db=db, transaction_id=transaction_id, user_id=current_user.id
    )
    if not transaction:
        logger.warning(f"Transaction {transaction_id} not found or not owned by user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction
