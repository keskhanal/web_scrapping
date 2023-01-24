The DealFlow database is implemented in MongoDB for the following reasons:

- Simple Pricing
- Flexible Records. This will allow us to keep source fields as well as standard fields in the same document.
- Easy to integrate


## DB Implementation

We are using MongoDB Atlas


### The Standard Schema for an incoming deal should have the following:

- CanonicalID (Required) -- This has to be a uniqueID that is constructed based on some offer. likely a hash for the marketplaceID + URL or something
- MarketplaceID (Required) -- This is the marketplaceID as defined by a list of marketpalces (should be normalized)
- Name (Required) -- Name of the asset 
- Description (Required) -- Description provided on the website
- URL (Required) -- URL for the asset
- Asking Price (Required) -- Asking Price  {amount: , currency: } (using price-parser}
- Asset Type --  What kind of asset? Content vs. SaaS, etc.
- Niche -- Which category / area? e.g. Finance
- Age
- Monthly Profit
- Profit Margin
- Profit Multiple
- Revenue Multiple



