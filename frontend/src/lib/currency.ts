/** Approximate USD → local rates for display (not live FX). Salaries are stored in USD. */
export const COUNTRY_CURRENCY: Record<string, string> = {
  "United States": "USD",
  "United Kingdom": "GBP",
  Germany: "EUR",
  France: "EUR",
  India: "INR",
  Canada: "CAD",
  Australia: "AUD",
  Japan: "JPY",
  Brazil: "BRL",
  Singapore: "SGD",
  Netherlands: "EUR",
  Sweden: "SEK",
};

/** Units of local currency per 1 USD */
export const USD_TO_LOCAL_RATE: Record<string, number> = {
  USD: 1,
  GBP: 0.79,
  EUR: 0.92,
  INR: 83.5,
  CAD: 1.36,
  AUD: 1.53,
  JPY: 149,
  BRL: 4.95,
  SGD: 1.34,
  SEK: 10.5,
};

export const BASE_CURRENCY = "USD";

export function getLocalCurrency(country: string): string {
  return COUNTRY_CURRENCY[country] ?? BASE_CURRENCY;
}

export function convertUsdToLocal(usdAmount: number, country: string): number {
  const localCurrency = getLocalCurrency(country);
  const rate = USD_TO_LOCAL_RATE[localCurrency] ?? 1;
  return usdAmount * rate;
}

export function convertLocalToUsd(localAmount: number, country: string): number {
  return convertLocalAmountToUsd(localAmount, getLocalCurrency(country));
}

export function convertLocalAmountToUsd(localAmount: number, currency: string): number {
  const rate = USD_TO_LOCAL_RATE[currency] ?? 1;
  if (rate === 0) return localAmount;
  return localAmount / rate;
}

export function getUsdRate(country: string): number {
  return USD_TO_LOCAL_RATE[getLocalCurrency(country)] ?? 1;
}

export function formatUsd(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: BASE_CURRENCY,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatLocalAmount(localAmount: number, country: string): string {
  const localCurrency = getLocalCurrency(country);
  return formatCurrencyCode(localAmount, localCurrency);
}

export function formatLocalSalary(usdAmount: number, country: string): string {
  return formatLocalAmount(convertUsdToLocal(usdAmount, country), country);
}

export function formatCurrencyCode(
  amount: number,
  currency: string,
  maximumFractionDigits = 0
): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits,
  }).format(amount);
}
