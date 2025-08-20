// --- Доменные модели ---

data class Money(val cents: Long, val currency: String) {
    init { require(cents >= 0) { "Money can't be negative" } }

    operator fun plus(other: Money): Money {
        require(currency == other.currency) { "Currency mismatch" }
        return Money(cents + other.cents, currency)
    }

    operator fun times(multiplier: Int): Money = copy(cents = cents * multiplier)

    fun format(): String = "%s %.2f".format(currency, cents / 100.0)
}

data class OrderItem(val name: String, val price: Money, val qty: Int) {
    fun lineTotal(): Money = price * qty
}

data class Order(
    val id: String,
    val items: List<OrderItem>,
    val currency: String
) {
    fun total(): Money =
        items.map { it.lineTotal() }.fold(Money(0, currency)) { acc, m -> acc + m }

    companion object {
        // Фабрика: быстро собрать заказ из пар (название, цена в центах, шт.)
        fun of(id: String, currency: String, vararg triples: Triple<String, Long, Int>): Order {
            val items = triples.map { (name, cents, qty) ->
                OrderItem(name, Money(cents, currency), qty)
            }
            return Order(id, items, currency)
        }
    }
}

// --- Результаты операций ---

sealed class PaymentResult {
    data class Success(val transactionId: String) : PaymentResult()
    data class Error(val reason: String) : PaymentResult()
}

// --- Стратегии оплаты ---

interface PaymentMethod {
    fun pay(amount: Money): PaymentResult
}

class CreditCard(private val numberMasked: String, private val limitCents: Long) : PaymentMethod {
    private var spent: Long = 0

    override fun pay(amount: Money): PaymentResult {
        if (amount.cents == 0L) return PaymentResult.Error("Zero amount")
        if (spent + amount.cents > limitCents) return PaymentResult.Error("Limit exceeded")
        spent += amount.cents
        return PaymentResult.Success("CC-$numberMasked-${System.currentTimeMillis()}")
    }
}

class PayPal(private val accountEmail: String) : PaymentMethod {
    override fun pay(amount: Money): PaymentResult =
        if (amount.cents > 0) PaymentResult.Success("PP-$accountEmail-${System.currentTimeMillis()}")
        else PaymentResult.Error("Zero amount")
}

// --- Репозиторий заказов ---

interface OrderRepository {
    fun save(order: Order)
    fun find(id: String): Order?
}

class InMemoryOrderRepository : OrderRepository {
    private val storage = mutableMapOf<String, Order>()
    override fun save(order: Order) { storage[order.id] = order }
    override fun find(id: String): Order? = storage[id]
}

// --- Сервис оформления и оплаты ---

class CheckoutService(
    private val repo: OrderRepository,
    private val defaultCurrency: String = "EUR"
) {
    fun checkout(order: Order, method: PaymentMethod, loyaltyDiscountPercent: Int = 0): PaymentResult {
        require(order.currency == defaultCurrency) { "Unsupported currency" }

        val total = order.total().discount(loyaltyDiscountPercent)
        val result = method.pay(total)

        if (result is PaymentResult.Success) {
            repo.save(order) // сохраняем только успешно оплаченные заказы
        }
        return result
    }
}

// --- Extension-функции ---

fun Money.discount(percent: Int): Money {
    if (percent <= 0) return this
    val capped = percent.coerceIn(0, 100)
    val discounted = cents - (cents * capped) / 100
    return copy(cents = discounted)
}

// Утилита для красивого вывода
fun PaymentResult.describe(amount: Money): String = when (this) {
    is PaymentResult.Success -> "Оплачено ${amount.format()}, транзакция #$transactionId"
    is PaymentResult.Error   -> "Оплата отклонена: $reason"
}

// --- Пример использования ---

fun main() {
    val repo = InMemoryOrderRepository()
    val checkout = CheckoutService(repo)

    val order = Order.of(
        id = "ORD-1001",
        currency = "EUR",
        Triple("Кофе", 350, 2),     // 3.50€ * 2
        Triple("Булочка", 199, 3)   // 1.99€ * 3
    )

    val method: PaymentMethod = CreditCard(numberMasked = "**** 1234", limitCents = 10_000)

    val result = checkout.checkout(order, method, loyaltyDiscountPercent = 10)

    println(result.describe(order.total().discount(10)))
    println("В репозитории: " + (repo.find("ORD-1001") != null))
}
