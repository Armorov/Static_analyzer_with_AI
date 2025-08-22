data class Money(val cents: Long, val currency: String) {
    init { require(cents >= 0) { "Money can't be negative" } }

    operator fun plus(other: Money): Money {
        require(currency == other.currency) { "Currency mismatch" }
        return Money(cents + other.cents, currency)
    }

    operator fun times(multiplier: Int): Money = copy(cents = cents * multiplier)

    fun format(): String = "%s %.2f".format(currency, cents / 100.0)
}
