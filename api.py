import Danbooru

# :)

#Danbooru
username = ""
api_key = ""

def main():
    danbooru_object = Danbooru.Danbooru(username, api_key)


    danbooru_list = danbooru_object.posts.get_n_random_posts(10,"ratio:6:19.5..12:19.5 ")
    danbooru_object.posts.make_csv_from_posts(danbooru_list)
    print(danbooru_object.posts.total_file_size(danbooru_list))
    danbooru_object.posts.save_posts(danbooru_list, "temp_iPhone")

    pass


main()