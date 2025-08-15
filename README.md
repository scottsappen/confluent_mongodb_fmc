# Confluent + MongoDB Atlas: Sink Embeddings with a Fully Managed Connector

<br>

# Overview
Ever wondered if you can push pre-built embeddings through Confluent and land them in MongoDB Atlas with no custom plumbing?

👉 The answer: Yes, you can.

This repo shows you how — in minutes, without complicated infra.

You will:
- 🚵 Generate mock mountain biking trail data
- 🔑 Create embeddings on the fly with OpenAI
- 📦 Publish events into Confluent Cloud Kafka
- 🌍 Sink data into MongoDB Atlas using Confluent’s Fully Managed Connector (FMC)

<br>

## 1. Prerequisites

- Confluent Cloud account  
- MongoDB Atlas account  
- OpenAI API key  
- Python 3 + pip  

> 💡 Tip: The Confluent Cloud UI has an **AI Assistant** that can answer setup questions or even generate code for you.  
> Remember to tear down your connector in Confluent Cloud to avoid getting charged.

<br>

## 2. Create a Kafka Topic

In Confluent Cloud:  
- Create a topic named **`trails_raw_data`**  
- (Or update your `.env` with a custom topic name)  

<br>

## 3. Configure Your Environment

- Edit [`.env`](./.env) with your **OpenAI credentials**  
- Edit [`client.properties`](./client.properties) with your **Confluent credentials**  
  - Unsure how? Go to **Clients → Producers → Set up new client** in Confluent Cloud to download a ready-to-use config  

## 4. Run the Data Generator

```bash
python3 producer_trails.py 1
```
- Replace `1` with the number of mock events you want to produce  
- Each record includes an embedding generated via OpenAI  

📄 Script: [`producer_trails.py`](./producer_trails.py)  

✅ If all goes well, you’ll see your events in the Confluent topic:  

<table>
  <tr>
    <td>
      <strong>`topic data`</strong><br>
      <a href="./screenshot1_cc_topic_trails.jpg" target="_blank">
        <img src="./screenshot1_cc_topic_trails.jpg" width="800"/>
      </a>
    </td>
  </tr>
</table>

<br>

## 5. Create the MongoDB Atlas Sink Connector

In Confluent Cloud:  
- Add a **MongoDB Atlas Sink Connector**  
- Provide your MongoDB Atlas connection string + credentials  

<table>
  <tr>
    <td>
      <strong>`fmc connector`</strong><br>
      <a href="./screenshot1_cc_mongosinkconnector.jpg" target="_blank">
        <img src="./screenshot1_cc_mongosinkconnector.jpg" width="800"/>
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="./screenshot2_cc_mongosinkconnector.jpg" target="_blank">
        <img src="./screenshot2_cc_mongosinkconnector.jpg" width="800"/>
      </a>
    </td>
  </tr>
</table>

<br>

## 6. Verify in MongoDB Atlas

Head over to your Atlas cluster → Collections.  

You should see your Kafka events flowing into your MongoDB collection (embeddings included 🎉).  

<table>
  <tr>
    <td>
      <strong>`mongodb atlas table`</strong><br>
      <a href="./screenshot3_mongo_db_trails.jpg" target="_blank">
        <img src="./screenshot3_mongo_db_trails.jpg" width="800"/>
      </a>
    </td>
  </tr>
</table>

<br>

## 7. Clean Up

Don’t forget to:  
- Delete the connector  
- Remove test topics if you don’t need them anymore  

This avoids surprise charges in Confluent Cloud or Atlas.  

<br>

## Wrap-Up

That’s it! You’ve proven you can:  
- Generate embeddings externally  
- Stream them through Confluent  
- Land them in MongoDB Atlas seamlessly  

Happy streaming 🚀  
