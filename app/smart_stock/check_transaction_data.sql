-- Check for case sensitivity issues and actual data values

-- 1. Show distinct transaction_type values (to catch case issues)
SELECT DISTINCT
    transaction_type,
    LENGTH(transaction_type) as length,
    LOWER(transaction_type) as lowercase,
    UPPER(transaction_type) as uppercase,
    COUNT(*) as count
FROM inventory_transactions
GROUP BY transaction_type
ORDER BY count DESC;

-- 2. Show distinct status values (to catch case issues)
SELECT DISTINCT
    status,
    LENGTH(status) as length,
    LOWER(status) as lowercase,
    UPPER(status) as uppercase,
    COUNT(*) as count
FROM inventory_transactions
GROUP BY status
ORDER BY count DESC;

-- 3. Check specifically for 'sale' vs 'Sale' vs 'SALE'
SELECT
    transaction_type,
    COUNT(*) as count
FROM inventory_transactions
WHERE LOWER(transaction_type) = 'sale'
GROUP BY transaction_type;

-- 4. Check the latest transactions you created
SELECT
    transaction_id,
    transaction_number,
    transaction_type,
    status,
    created_at,
    transaction_timestamp
FROM inventory_transactions
ORDER BY transaction_id DESC
LIMIT 5;

-- 5. Check if the parent callback is enabled (this would refresh data)
-- Look at the console for any errors when creating transactions