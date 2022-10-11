import requests, csv, random, re, common_defs
from PIL import Image

# :)

class Danbooru:
    def __init__(self, given_username, given_api_key) -> None:
        self._base_url = "https://danbooru.donmai.us/"
        #self._test_base_url = "https://testbooru.donmai.us/" doesn't work unless you make seperate account on this site (use for upload testing)

        self._session = requests.session()
        self._username = given_username
        self.__api_key = given_api_key
        self._user_agent = {"User-Agent": "MyProject ({})".format(self._username)}
        self._basic_auth = (self._username, self.__api_key)

        self._special_blacklisted_tags = "-status:banned rating:g" + " "
        self._blacklisted_tags = ["animated", "spoilers", "flash", "samsung_sam"]
        self._common_search_tags = ["fav:{}".format(self._username)]
        self._default_search_tags = "score:>50 "

        #self.initialize_dirs()
        self.posts = self.Posts(self)
        pass


    def initialize_dirs(self) -> None:
        common_defs.make_dirs("Downloads/Danbooru/General")

    def get_profile_info(self):
        response = self._session.get(self._base_url + "profile.json", auth=self._basic_auth, headers=self._user_agent)
        return response.json()
    
    class Posts:
        def __init__(self, danbooru_object) -> None:
            self.object = danbooru_object
            pass

        def get_1_posts(self, search_tags="") -> list:
            search_tags = self.tag_check(search_tags, "random:1 ")

            payload = {"limit": 1, "tags": search_tags + self.object._special_blacklisted_tags}
            response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)
            print("\nGot {} post from Danbooru.".format(len(response.json())))
            return response.json()

        def get_n_posts(self, ammount=1, search_tags="") -> list:
            posts_list = []
            search_tags = self.tag_check(search_tags)
            payload = {"limit": 200, "tags": search_tags + self.object._special_blacklisted_tags}
            response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)

            while response.json() != []:
                lowest_id = response.json()[-1]["id"]
                repeat_ammount = 0

                full_post_list_flag, limit = self.ammount_checker(ammount, posts_list)

                for post in response.json()[:limit]:
                        if self.check_if_post_safe(post) == True:
                            posts_list.append(post)
                        else:
                            repeat_ammount += 1
                if len(posts_list) >= ammount:
                    print("\nReturned {} posts from Danbooru".format(len(posts_list)))
                    return posts_list

                elif full_post_list_flag == False:
                    print("Because of {} blacklisted posts, checking remainder {} posts for {} posts".format(repeat_ammount, len(response.json())-limit, ammount-len(posts_list)))
                    count = 0
                    for post in response.json()[limit:]:
                        count += 1
                        if self.check_if_post_safe(post) == True:
                            posts_list.append(post)
                            if len(posts_list) >= ammount:
                                print("\nReturned {} posts from Danbooru after checking {} additional posts".format(len(posts_list), count))
                                return posts_list
                        else:
                            repeat_ammount += 1

                print("{}% done ({} out of {} total posts fetched)".format(round(len(posts_list)*100/ammount, 2), len(posts_list), ammount))
                print("{}% discarded ({} posts were blacklisted out of {} posts fetched)".format(round(repeat_ammount*100/len(response.json()), 2), repeat_ammount, len(response.json())))

                payload = {"limit": 200, "tags": search_tags + self.object._special_blacklisted_tags, "page": "b{}".format(lowest_id)}
                response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)

            print("\nReturned only {} posts from Danbooru out of the requested {}!".format(len(posts_list), ammount))
            return posts_list

        def get_n_random_posts(self, ammount=1, search_tags="", threshold=0.75, full_check=True) -> list:
            posts_list = []
            id_set = set()
            search_tags = self.tag_check(search_tags)

            if full_check == True:
                full_check_posts = self.object.Posts.get_n_posts(self, ammount, search_tags)
                if len(full_check_posts) < ammount:
                    print("\nOnly {} posts on Danbooru fitting given criteria out of the requested {}\nReturning those posts (not in random order)".format(len(full_check_posts), ammount))
                    return full_check_posts
                else:
                    print("\nAt least {} posts on Danbooru fitting given criteria\nStarting random search without failsafe".format(len(full_check_posts)))
                    threshold = 100

            payload = {"limit": 200, "tags": search_tags + self.object._special_blacklisted_tags + "order:random "}
            response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)

            while response.json() != []:
                repeat_ammount = 0
                blacklist_ammount = 0

                full_post_list_flag, limit = self.ammount_checker(ammount, posts_list)
                
                for post in response.json()[:limit]:
                    if not post["id"] in id_set:
                        id_set.add(post["id"])
                        if self.check_if_post_safe(post) == True:
                            posts_list.append(post)
                        else: 
                            blacklist_ammount += 1
                    else:
                        repeat_ammount += 1

                if len(posts_list) >= ammount:
                    print("\nReturned {} posts from Danbooru".format(len(posts_list)))
                    return posts_list

                elif full_post_list_flag == False:
                    print("Because of {} duplicates/blacklisted posts, checking remainder {} posts for {} posts".format(repeat_ammount + blacklist_ammount, len(response.json())-limit, ammount-len(posts_list)))
                    count = 0
                    for post in response.json()[limit:]:
                        count += 1
                        if not post["id"] in id_set:
                            id_set.add(post["id"])
                            if self.check_if_post_safe(post) == True:
                                posts_list.append(post)
                                if len(posts_list) >= ammount:
                                    print("\nReturned {} posts from Danbooru after checking {} additional posts".format(len(posts_list), count))
                                    return posts_list
                            else:
                                blacklist_ammount += 1
                        else:
                            repeat_ammount += 1

                if repeat_ammount/len(response.json()) > threshold:
                    print("\nReturned {} posts out of the requested {} from Danbooru\nmore than {}% of the posts were duplicates/blacklisted in the last search!\n{} of the {} ({}%) last fetched were duplicates!".format(len(posts_list), ammount, threshold*100, repeat_ammount, len(response.json()), round(repeat_ammount*100/len(response.json()), 2)))
                    return posts_list
                
                print("{}% done ({} out of {} total posts fetched)".format(round(len(posts_list)*100/ammount, 2), len(posts_list), ammount))
                print("{}% discarded ({} posts were duplicates/blacklisted out of {} posts fetched)".format(round((repeat_ammount + blacklist_ammount)*100/len(response.json()), 2), repeat_ammount + blacklist_ammount, len(response.json())))
                print("{}% repeat rate ({} posts were actualy repeats)".format(round((repeat_ammount)*100/len(response.json()), 2), repeat_ammount))

                payload = {"limit": 200, "tags": search_tags + self.object._special_blacklisted_tags + "order:random "}
                response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)

            print("\nNo results from Danbooru for these search tags!".format(len(posts_list), ammount))
            return posts_list
        
        def ammount_checker(self, ammount, posts_list):
            if ammount - len(posts_list) < 200:
                limit = ammount - len(posts_list)
                full_post_list_flag = False
                print("\nChecking {} posts".format(limit))
            else:
                limit = 201
                full_post_list_flag = True
                print("\nChecking {} posts".format(200))
            return full_post_list_flag, limit

        def get_all_posts(self, search_tags="") -> list:
            return self.get_all(search_tags)

        def get_all_favorites(self, search_tags="") -> list:
            return self.get_all(search_tags, "fav:{} ".format(self.object._username))

        def get_all(self, search_tags="", extra_tags="") -> list:
            posts_list = []
            search_tags = self.tag_check(search_tags)

            payload = {"limit": 200, "tags": search_tags + self.object._special_blacklisted_tags + extra_tags}
            response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)

            while response.json() != []:
                valid_posts = self.remove_blacklisted_posts(response.json())
                posts_list.extend(valid_posts)
                lowest_id = response.json()[-1]["id"]
                print("\n{} posts fetched of which {} were valid\nLowest id: {}\n{} posts in list now".format(len(response.json()), len(valid_posts), lowest_id, len(posts_list)))
                payload = {"limit": 200, "tags": search_tags + self.object._special_blacklisted_tags + extra_tags, "page": "b{}".format(lowest_id)}
                response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)
            print("\nReturned {} posts from Danbooru".format(len(posts_list)))
            return posts_list

        def get_post_from_id(self, id_list) -> list:
            post_list = []
            for id in id_list:
                payload = {"limit": 1, "tags": "id:{}".format(id)}
                print("Getting id:{}".format(id))
                response = self.object._session.get(self.object._base_url + "posts.json", auth=self.object._basic_auth, headers=self.object._user_agent, params=payload)
                post_list.extend(response.json())
            print("\nGot {} posts from Danbooru out of the requested {}".format(len(post_list), len(id_list)))
            return post_list
        
        def remove_blacklisted_posts(self, post_list) -> list:
            return_post_list = []
            chosen = False
            removed_posts = 0

            for post in post_list:
                for tag in self.object._blacklisted_tags:
                    if re.search(r"\b"+ tag + r"\b", post["tag_string"]) == None:
                        chosen = True
                        continue
                    else:
                        #print("post had {} in it".format(tag))
                        chosen = False
                        break
                if chosen == True and post["is_banned"] == False:
                    return_post_list.append(post)
                else:
                    removed_posts += 1
            #print("\nReturned {} posts\nRemoved {} posts".format(len(return_post_list),removed_posts))
            return return_post_list

        def check_if_post_safe(self, post:dict) -> bool:
            for tag in self.object._blacklisted_tags:
                if re.search(r"\b"+ tag + r"\b", post["tag_string"]) == None:
                    continue
                else:
                    #print("post had {} in it".format(tag))
                    return False
            if post["is_banned"] == False:
                return True
            else:
                return False

        def tag_check(self, search_tags, extra_tags="") -> str:
            if search_tags == "":
                return self.object._default_search_tags + extra_tags
            else:
                for tag in self.object._blacklisted_tags:
                    if not re.search(r"\b"+ tag + r"\b", search_tags) == None:
                        print(re.search(r"\b"+ tag + r"\b", search_tags))
                        raise Exception("\nGiven search tag ({}) is also in the blacklisted tags ({})!\nGiven search tags: {}".format(tag, self.object._blacklisted_tags, search_tags))
                return search_tags

        def make_csv_from_posts(self, posts_list, csv_name="placeholder.csv") -> None:
            fields = []
            rows = []
            for key in posts_list[0].keys():
                fields.append(key)
            for post in posts_list:
                post_row = []
                for value in post.values():
                    post_row.append(value)
                rows.append(post_row)
            with open(csv_name, "w", newline='', encoding="utf-8") as file:
                csv.writer(file).writerow(fields)
                csv.writer(file).writerows(rows)
            print("{} ready!".format(csv_name))
        
        def show_posts(self, posts_list, ammount=0, random_show=False) -> None:
            if ammount == 0:
                i = len(posts_list)
            else:
                i = ammount

            count = 0
            if random_show == False:
                for post in posts_list[:i]:
                    count += 1
                    Image.open(requests.get(post["file_url"], stream=True).raw).show()
                    print("Showing post #{}".format(count))
                print("\nShowed first {} posts\n{} posts were given (from Danbooru)".format(count, len(posts_list)))

            else: #random_show == True
                post_number_set = set()
                post_number = random.randint(0, len(posts_list) -1)
                while count < i:
                    count += 1
                    while post_number in post_number_set:
                        post_number = random.randint(0, len(posts_list) -1) #dumb cant exclude
                    Image.open(requests.get(posts_list[post_number]["file_url"], stream=True).raw).show()
                    print("Showing post #{} (out of {} posts)".format(post_number +1, len(posts_list)))
                    post_number_set.add(post_number)
                print("\nShowed {} random posts\n{} posts were given (from Danbooru)".format(count, len(posts_list)))

        def save_posts(self, posts_list, path="Danbooru", make_rating_dirs=False) -> None:
            count = 0
            path = "Downloads/" + path

            if make_rating_dirs == True:
                common_defs.make_dirs("{}/General".format(path))
                for post in posts_list:
                    count += 1
                    rating = "General"
                    print("Saving post #{} out of {} posts ({}% done)".format(count, len(posts_list), round(count*100/len(posts_list), 2)))
                    Image.open(requests.get(post["file_url"], stream=True).raw).save(fp="{}/{}/{}.{}".format(path, rating, post["id"], post["file_ext"]))
                print('\nsaved {} images from Danbooru to "{}"'.format(count, path))
            
            else:
                common_defs.make_dirs("{}".format(path))
                for post in posts_list:
                    count += 1
                    print("Saving post #{} out of {} posts ({}% done)".format(count, len(posts_list), round(count*100/len(posts_list), 2)))
                    Image.open(requests.get(post["file_url"], stream=True).raw).save(fp="{}/{}.{}".format(path, post["id"], post["file_ext"]))
                print('\nsaved {} images from Danbooru to "{}"'.format(count, path))



        def return_urls(self, posts_list) -> list:
            url_list = []
            for post in posts_list:
                url_list.append(post["file_url"])
            return url_list
        
        def total_file_size(self, posts_list) -> int:
            total_size = 0
            for post in posts_list:
                total_size += post["file_size"]
            return total_size

        # def get_and_show_n_posts(self, ammount=1, search_tags=""):
        #     Danbooru.Posts.show_posts(self, Danbooru.Posts.get_n_posts(self, ammount, search_tags))

# def make_tags_string(tupled_tags):
#     tag_string = ""
#     for tag in tupled_tags:
#         tag_string += tag + " "
#     return tag_string

# def make_dirs(dir_path):
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)