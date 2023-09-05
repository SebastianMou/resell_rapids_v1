// ################################## amazon calculate ################################

function calculate() {
    const productPrice = parseFloat(document.getElementById('productPrice').value);
    const taxRate = parseFloat(document.getElementById('taxRate').value) / 100;
    const productCost = parseFloat(document.getElementById('productCost').value);
    const additionalUnitCost = parseFloat(document.getElementById('additionalUnitCost').value);
    const additionalMonthlyCosts = parseFloat(document.getElementById('additionalMonthlyCosts').value);
    const estMonthlySales = parseFloat(document.getElementById('estMonthlySales').value);

    const sellingPriceAfterTaxes = productPrice + (productPrice * taxRate);
    const totalFBAFee = productCost + additionalUnitCost + additionalMonthlyCosts;
    const profitPerUnit = sellingPriceAfterTaxes - totalFBAFee;
    const netMargin = (profitPerUnit / sellingPriceAfterTaxes) * 100;
    const roi = (profitPerUnit / totalFBAFee) * 100;
    const estMonthlyProfit = profitPerUnit * estMonthlySales;

    document.getElementById('totalFBAFee').textContent = totalFBAFee.toFixed(2);
    document.getElementById('profitPerUnit').textContent = profitPerUnit.toFixed(2);
    document.getElementById('netMargin').textContent = netMargin.toFixed(2);
    document.getElementById('roi').textContent = roi.toFixed(2);
    document.getElementById('estMonthlyProfit').textContent = estMonthlyProfit.toFixed(2);
}
// ##################################################################
class Calculator {
    constructor(previousOperandTextElement, currentOperandTextElement) {
        this.previousOperandTextElement = previousOperandTextElement
        this.currentOperandTextElement = currentOperandTextElement
        this.clear()
    }

    clear() {
        this.currentOperand = ''
        this.previousOperand = ''
        this.operation = undefined
    }

    delete() {
        this.currentOperand = this.currentOperand.toString().slice(0, -1)
    }

    appendNumber(number) {
        if (number === '.' && this.currentOperand.includes('.')) return
        this.currentOperand = this.currentOperand.toString() + number.toString()
    }

    chooseOperation(operation) {
        if (this.currentOperand === '') return
        if (this.previousOperand !== '') {
            this.compute()
        }
        this.operation = operation
        this.previousOperand = this.currentOperand
        this.currentOperand = ''
    }

    compute() {
        let computation
        const prev = parseFloat(this.previousOperand)
        const current = parseFloat(this.currentOperand)
        if (isNaN(prev) || isNaN(current)) return
        switch (this.operation) {
            case '÷':
                computation = prev / current
                break
            case 'x':
                computation = prev * current
                break
            case '+':
                computation = prev + current
                break
            case '-':
                computation = prev - current
                break
            default:
                return
        }
        this.currentOperand = computation
        this.operation = undefined
        this.previousOperand = ''
    }

    getDisplayNumber(number) {
        const stringNumber = number.toString()
        const integerDisplay = parseFloat(stringNumber.split('.')[0])
        const decimalDigits = stringNumber.split('.')[1]
        let intigerDisplay
        if (isNaN(integerDisplay)) {
            intigerDisplay = ''
        } else {
            intigerDisplay = integerDisplay.toLocaleString('en', {
                maximumFractionDigits: 0
            })
        }
        if (decimalDigits != null) {
            return `${intigerDisplay}.${decimalDigits}`
        } else {
            return intigerDisplay
        }
    }

    updateDisplay() {
        this.currentOperandTextElement.innerText = this.getDisplayNumber(this.currentOperand)
        if (this.operation != null) {
            this.previousOperandTextElement.innerText = `${this.previousOperand} ${this.operation}`;
        } else {
            this.previousOperandTextElement.innerText = ''
        }
    }
}

const numberButtons = document.querySelectorAll('[data-number]')
const operationButtons = document.querySelectorAll('[data-operation]')
const equalsButton = document.querySelector('[data-equals]')
const deleteButton = document.querySelector('[data-delete]')
const allClearButton = document.querySelector('[data-all-clear]')
const previousOperandTextElement = document.querySelector('[data-previous-operand]')
const currentOperandTextElement = document.querySelector('[data-current-operand]')

const calculator = new Calculator(previousOperandTextElement, currentOperandTextElement)

numberButtons.forEach(button => {
    button.addEventListener('click', () => {
        calculator.appendNumber(button.innerText)
        calculator.updateDisplay()
    })
})

operationButtons.forEach(button => {
    button.addEventListener('click', () => {
        calculator.chooseOperation(button.innerText)
        calculator.updateDisplay()
    })
})

equalsButton.addEventListener('click', button => {
    calculator.compute()
    calculator.updateDisplay()
})

allClearButton.addEventListener('click', button => {
    calculator.clear()
    calculator.updateDisplay()
})

deleteButton.addEventListener('click', button => {
    calculator.delete()
    calculator.updateDisplay()
})

// dropdown
function toggleDropdown() {
    const dropdownContent = document.getElementById("dropdownContent");
    dropdownContent.classList.toggle("show");
}
