export class MockBackend {
  async lendees(lendee: string) {
    return Promise.resolve({
      balance_json: null,
      name: "John Doe",
      verdict_json: {
        cons: [
          "Frequent ATM cash withdrawals might indicate a heavy reliance on cash transactions which could be inefficient.",
          "Charges associated with ATM withdrawals and other service charges could indicate potential areas for more efficient banking practices.",
          "Regular debits for Bajaj Finance suggesting ongoing liability or loans which may impact financial flexibility.",
        ],
        pros: [
          "Consistent and regular transaction history indicating steady business operations.",
          "Presence of quarterly savings interest credits suggesting sound savings habit.",
          "Diversified transactions including bills, fund transfers, and regular vendor payments indicating a well-rounded financial management.",
        ],
      },
    });
  }
}
